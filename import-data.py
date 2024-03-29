import json
import os
import urllib3
import sys
import pathlib


class RepoBranchProtection:
    def __init__(self, repo_bp):
        self.repo_bp = repo_bp
        self.signed_commits = repo_bp.get("required_signatures", {}).get(
            "enabled", False
        )
        self.enforce_admins = repo_bp.get("enforce_admins", {}).get(
            "enabled", True
        )
        self.required_conversation_resolution = repo_bp.get(
            "required_conversation_resolution", {}
        ).get("enabled", False)

        self.required_status_checks = self.status_checks()
        self.required_pull_request_reviews = self.pull_request_reviews()
        self.restrictions = self.restricts()

    def status_checks(self):
        req_stat_checks = self.repo_bp.get("required_status_checks", {})
        req_strict = req_stat_checks.get("strict", True)
        req_checks = req_stat_checks.get("checks", [])

        formatted_checks = [
            check["context"]
            if check["app_id"] is None
            else f'{check["context"]}:{check["app_id"]}'
            for check in req_checks
        ]

        req_stat_checks["checks"] = formatted_checks
        req_stat_checks.pop("contexts", None)
        req_stat_checks["strict"] = req_strict

        return req_stat_checks

    def pull_request_reviews(self):
        req_pr_reviews = self.repo_bp.get("required_pull_request_reviews", {})
        req_review_count = req_pr_reviews.get(
            "required_approving_review_count", 1
        )
        req_pr_reviews["required_approving_review_count"] = req_review_count

        if "dismissal_restrictions" in req_pr_reviews:
            dis_restrict_users = req_pr_reviews["dismissal_restrictions"].get(
                "users", []
            )
            dis_restrict_teams = req_pr_reviews["dismissal_restrictions"].get(
                "teams", []
            )

            dis_users = [
                user["login"]
                for user in dis_restrict_users
                if isinstance(user, dict)
            ]
            dis_teams = [
                team["slug"]
                for team in dis_restrict_teams
                if isinstance(team, dict)
            ]
            req_pr_reviews["dismissal_users"] = dis_users
            req_pr_reviews["dismissal_teams"] = dis_teams

        if "bypass_pull_request_allowances" in req_pr_reviews:
            pr_allow_users = req_pr_reviews[
                "bypass_pull_request_allowances"
            ].get("users", [])

            pr_allow_teams = req_pr_reviews[
                "bypass_pull_request_allowances"
            ].get("teams", [])

            bypass_pr_allow_users = [
                user["login"]
                for user in pr_allow_users
                if isinstance(user, dict)
            ]
            bypass_pr_allow_teams = [
                team["slug"]
                for team in pr_allow_teams
                if isinstance(team, dict)
            ]

        # rewrite required_pull_request_reviews["bypass_pull_request_allowances"]["users"] as lists
        # rewrite required_pull_request_reviews["bypass_pull_request_allowances"]["users"] as lists
        if "bypass_pull_request_allowances" in req_pr_reviews:
            req_pr_reviews["bypass_pull_request_allowances"][
                "users"
            ] = bypass_pr_allow_users

            # rewrite required_pull_request_reviews["bypass_pull_request_allowances"]["teams"] as lists
            req_pr_reviews["bypass_pull_request_allowances"][
                "teams"
            ] = bypass_pr_allow_teams

        return req_pr_reviews

    def restricts(self):
        restrictions_data = self.repo_bp.get("restrictions", {})
        restrictions = {}

        if restrictions_data:
            restrict_users = restrictions_data.get("users", [])
            restrict_teams = restrictions_data.get("teams", [])
            restrictions_users = [user["login"] for user in restrict_users]
            restrictions_teams = [team["slug"] for team in restrict_teams]

            if restrictions_users:
                restrictions["users"] = restrictions_users
            if restrictions_teams:
                restrictions["teams"] = restrictions_teams

        return restrictions


def get_members() -> None:
    """
    Get a list of members in the organization.
    """

    all_members = github_api_request(f"/orgs/{org}/members")
    users_array = [user["login"] for user in all_members]

    # Get the role of each user in the organization.
    users_data = []
    for user in users_array:
        data = github_api_request(f"/orgs/{org}/memberships/{user}")
        # JSON schema
        user_data = {"username": data["user"]["login"], "role": data["role"]}
        users_data.append(user_data)

    MEMBERS_OUTPUT = "members.json"
    with open(MEMBERS_OUTPUT, "w") as f:
        json.dump(users_data, f, indent=4)

    print(f"\nList of members written to {MEMBERS_OUTPUT}\n")


def get_teams() -> None:
    """
    Get a list of teams in the organization.
    """

    data = github_api_request(f"/orgs/{org}/teams")

    teams_data = []
    for team in range(len(data)):
        name = data[team]["name"]
        team_id = data[team]["id"]
        description = (
            data[team]["description"] if data[team]["description"] else None
        )
        privacy = data[team]["privacy"]
        parent_team_id = (
            data[team]["parent"]["id"] if data[team]["parent"] else None
        )
        slug = data[team]["slug"]

        # JSON schema
        team_data = {
            "name": name,
            "id": team_id,
            "description": description,
            "privacy": privacy,
            "parent_team_id": parent_team_id,
            "slug": slug,
        }

        teams_data.append(team_data)

    TEAMS_JSON = "teams.json"
    with open(TEAMS_JSON, "w") as f:
        json.dump(teams_data, f, indent=4)

    print(f"\nList of teams written to {TEAMS_JSON}\n")


def get_team_membership() -> None:
    """
    Get a list of teams in the organization and their members and roles.
    Writes to a single JSON file, indicated by TEAMS_MEMBERSHIP_JSON.
    """

    teams_json = github_api_request(f"/orgs/{org}/teams")

    # JSON schema
    teams = []
    for team in range(len(teams_json)):
        teams.append(
            {
                "id": teams_json[team]["id"],
                "name": teams_json[team]["name"],
                "slug": teams_json[team]["slug"],
                "members": [],
            }
        )

    # For each team, get a list of its members
    for team in teams:
        members_json = github_api_request(
            f"/orgs/{org}/teams/{team['slug']}/members"
        )
        # For each member, get their role in the team
        for member in members_json:
            membership_json = github_api_request(
                f"/teams/{team['id']}/memberships/{member['login']}"
            )
            team_member_role = membership_json["role"]
            team["members"].append(
                {"username": member["login"], "role": team_member_role}
            )

    TEAM_MEMBERSHIP_JSON = "team-membership.json"
    with open(TEAM_MEMBERSHIP_JSON, "w") as f:
        json.dump(teams, f, indent=4)

    print(f"\nList of team membership written to {TEAM_MEMBERSHIP_JSON}\n")


def get_team_membership_files() -> None:
    """
    Get a list of teams in the organization and their members and roles.
    Writes team data to individual JSON files and stored in TEAMS_FOLDER.
    """

    TEAMS_FOLDER = "team-membership/"

    print(f'Checking if the folder "{TEAMS_FOLDER}" exists\n')
    if not pathlib.Path(TEAMS_FOLDER).is_dir():
        print(f"Creating {TEAMS_FOLDER}")
        pathlib.Path(TEAMS_FOLDER).mkdir(parents=True, exist_ok=True)
    else:
        print(f'Folder "{TEAMS_FOLDER}" already exists\n')
        print(f"Deleting all files in {TEAMS_FOLDER}\n")
        for file in pathlib.Path(TEAMS_FOLDER).glob("*"):
            if file.is_file():
                file.unlink()

    teams_json = github_api_request(f"/orgs/{org}/teams")

    # JSON schema
    teams = []
    for team in range(len(teams_json)):
        teams.append(
            {
                "id": teams_json[team]["id"],
                "name": teams_json[team]["name"],
                "slug": teams_json[team]["slug"],
                "members": [],
            }
        )

    team_files = []

    # For each team, get a list of its members
    for team in teams:
        team_files.append(team["slug"] + ".json")
        members_json = github_api_request(
            f"/orgs/{org}/teams/{team['slug']}/members"
        )
        # For each member, get their role in the team
        for member in members_json:
            membership_json = github_api_request(
                f"/teams/{team['id']}/memberships/{member['login']}"
            )
            team_member_role = membership_json["role"]
            team["members"].append(
                {"username": member["login"], "role": team_member_role}
            )

    # Write team data to individual files
    for team in range(len(team_files)):
        with open(f"{TEAMS_FOLDER}{team_files[team]}", "w") as f:
            json.dump(teams[team], f, indent=4)

    print(f"\nList of team membership information written to {TEAMS_FOLDER}\n")


def create_directory(dir_path: pathlib.Path) -> None:
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
        print(f'The directory "./{str(dir_path)}" was created.')
    else:
        print(f'The directory "./{str(dir_path)}" already exists.')


def write_list_to_file(file_path, data_list):
    with open(file_path, "w") as file:
        for item in data_list:
            file.write(str(item) + "\n")


def get_branch_protection() -> None:
    """
    Queries all GitHub repositories belonging to a specific organization for
    information and writes the repository information to individual JSON files,
    where each file name is the name of the repository.
    """

    dir_path = pathlib.Path("branch-protection")
    full_data_dir_path = pathlib.Path("branch-protection-full-data")
    create_directory(dir_path)
    create_directory(full_data_dir_path)

    repos = get_organization_repos()

    not_protected = []
    protected = []
    failed_repo = []

    for repo in repos:
        repo_name = repo["name"]
        def_branch = repo["default_branch"]
        file_name = repo_name + ".json"
        full_data_file_name = repo_name + "_full_data.json"

        bp_data = github_api_request(
            f"/repos/{org}/{repo_name}/branches/{def_branch}/protection"
        )

        # use class to determine branch protection rules
        repobp = RepoBranchProtection(bp_data)

        if (
            "message" in bp_data
            and bp_data["message"] == "Branch not protected"
        ):
            print(f"No branch protection: {repo_name}:{def_branch}")
            not_protected.append(repo_name)
        elif "url" in bp_data:
            print(f"Branch protection: {repo_name}:{def_branch}")
            protected.append(repo_name)
        else:
            print(f"Branch protection error: {repo_name}:{def_branch}")
            failed_repo.append(repo_name)

        with open(f"{full_data_dir_path}/{full_data_file_name}", "w") as file:
            json.dump(bp_data, file, indent=4)

        # JSON schema
        repo_data = {
            "repository": repo_name,
            "branch": def_branch,
            "enforce_admins": repobp.enforce_admins,
            "require_signed_commits": repobp.signed_commits,
            "require_conversation_resolution": repobp.required_conversation_resolution,
            "required_status_checks": repobp.required_status_checks,
            "required_pull_request_reviews": repobp.required_pull_request_reviews,
        }

        # add restrictions key only if it is not None
        if repobp.restrictions:
            repo_data["restrictions"] = repobp.restrictions

        # Write the repository data to a JSON file
        with open(dir_path / file_name, "w") as file:
            json.dump(repo_data, file, indent=4)

    print(f"failed repos: {failed_repo}")
    print(f"protected repos: {protected}")
    print(f"not protected repos: {not_protected}")

    if failed_repo:
        write_list_to_file("bp-errors.txt", failed_repo)

    if not_protected:
        write_list_to_file("bp-not-protected.txt", not_protected)

    print(
        f"\nRepository terraform data is written to the directory ./{dir_path}.\n"
    )
    print(
        f"Repository full api data is written to the directory ./{full_data_dir_path}.\n"
    )


def get_repos() -> None:
    """
    Queries all GitHub repositories belonging to a specific organization for
    information and writes the repository information to individual JSON files,
    where each file name is the name of the repository.
    """

    dir_path = pathlib.Path("repos")
    full_data_dir_path = pathlib.Path("repos-full-data")
    create_directory(dir_path)
    create_directory(full_data_dir_path)

    repos = get_organization_repos()

    # for repo in data:
    for repo in repos:
        repo_name = repo["name"]
        file_name = repo_name + ".json"
        full_data_file_name = repo_name + "_full_data.json"

        # Query the /repos/{owner}/{repo} endpoint
        repo_data = github_api_request(f"/repos/{org}/{repo_name}")

        with open(f"{full_data_dir_path}/{full_data_file_name}", "w") as f:
            json.dump(repo_data, f, indent=4)

        # Loop through each repository and extract the relevant information
        # for repo in repo_data:
        repo_info = {
            "name": repo_data["name"],
            "description": repo_data["description"],
            "homepage_url": repo_data["homepage"],
            "private": repo_data["private"],
            "visibility": repo_data["visibility"],
            "has_issues": repo_data["has_issues"],
            "has_discussions": repo_data["has_discussions"],
            "has_projects": repo_data["has_projects"],
            "has_wiki": repo_data["has_wiki"],
            "is_template": repo_data["is_template"],
            "allow_merge_commit": repo_data["allow_merge_commit"],
            "allow_squash_merge": repo_data["allow_squash_merge"],
            "allow_rebase_merge": repo_data["allow_rebase_merge"],
            "allow_auto_merge": repo_data["allow_auto_merge"],
            "squash_merge_commit_title": repo_data[
                "squash_merge_commit_title"
            ],
            "squash_merge_commit_message": repo_data[
                "squash_merge_commit_message"
            ],
            "merge_commit_title": repo_data["merge_commit_title"],
            "merge_commit_message": repo_data["merge_commit_message"],
            "delete_branch_on_merge": repo_data["delete_branch_on_merge"],
            "has_downloads": repo_data["has_downloads"],
            # "auto_init": repo_data["auto_init"],
            # "gitignore_template": repo_data["gitignore_template"],
            # "license_template": repo_data["license_template"],
            "default_branch": repo_data["default_branch"],
            "archived": repo_data["archived"],
            # "archive_on_destroy": repo_data["archive_on_destroy"],
            "pages:": repo_data.get("pages", {}),
            "security_and_analysis": repo_data.get(
                "security_and_analysis", {}
            ),
            "topics": repo_data.get("topics", []),
            # "template": repo_data.get("template", {}),
            "vulnerability_alerts": repo_data.get("vulnerability_alerts"),
            # "ignore_vulnerability_alerts_during_read": repo_data.get(
            # "ignore_vulnerability_alerts_during_read"
            # ),
            "allow_update_branch": repo_data["allow_update_branch"],
        }
        with open(f"{str(dir_path)}/{file_name}", "w") as f:
            json.dump(repo_info, f, indent=4)

    print(
        f"\nRepository terraform data is written to the directory ./{dir_path}.\n"
    )
    print(
        f"Repository full api data is written to the directory ./{full_data_dir_path}.\n"
    )


def get_organization_repos():
    # Get all repos from the organization
    all_repos = github_api_request(f"/orgs/{org}/repos")

    # Filter only non-archived repos
    non_archived_repos = [
        repo for repo in all_repos if not repo.get("archived", False)
    ]

    return non_archived_repos


def get_collaborators(repo_name):
    # Get all collaborators from a repo
    collaborators_data = github_api_request(
        f"/repos/{org}/{repo_name}/collaborators"
    )

    collaborators = []
    for data in collaborators_data:
        collaborators.append(
            {
                "name": data.get("login"),
                "permissions": data.get("permissions", {}),
            }
        )

    return collaborators


def get_collaborators_teams(repo_name):
    # Get all teams associated with a repo
    teams_data = github_api_request(f"/repos/{org}/{repo_name}/teams")

    teams = []
    for data in teams_data:
        teams.append(
            {
                "name": data.get("slug"),
                "permissions": data.get("permissions", {}),
            }
        )

    return teams


def get_highest_permission(permissions):
    permission_order = ["admin", "maintain", "push", "triage", "pull"]

    for permission in permission_order:
        if permissions.get(permission, False):
            return permission

    return None


def get_team_members(team_name):
    # Get all members of a team
    members_data = github_api_request(f"/orgs/{org}/teams/{team_name}/members")

    members = [data.get("login") for data in members_data]

    return members


def get_organization_owners():
    all_members = github_api_request(f"/orgs/{org}/members")
    owners = []
    for member in all_members:
        username = member.get("login")
        user_membership = github_api_request(
            f"/orgs/{org}/memberships/{username}"
        )
        if user_membership.get("role") == "admin":
            owners.append(username)
    return owners


def get_repo_collaborators() -> None:
    repos = get_organization_repos()

    # Get all the organization owners
    org_owners = get_organization_owners()
    print(f"Organization owners: {org_owners}")

    all_collaborators_and_teams = {}
    for repo in repos:
        repo_name = repo.get("name")
        collaborators = get_collaborators(repo_name)
        teams = get_collaborators_teams(repo_name)

        repo_entry = all_collaborators_and_teams.setdefault(
            repo_name, {"users": [], "teams": []}
        )

        # Create a dictionary to store team members and their permissions
        team_members_permissions = {}

        # Create a dictionary to store team permissions and members
        for team in teams:
            permissions = team.get("permissions", {})
            highest_permission = get_highest_permission(permissions)
            members = get_team_members(team.get("name"))

            # Add the members and their permissions to the dictionary
            for member in members:
                team_members_permissions[member] = highest_permission

            repo_entry["teams"].append(
                {
                    "team_id": team.get("name"),
                    "permission": highest_permission,
                }
            )

        print(f"Team members for {repo_name}: {team_members_permissions}")

        for collaborator in collaborators:
            permissions = collaborator.get("permissions", {})
            highest_permission = get_highest_permission(permissions)
            collaborator_name = collaborator.get("name")

            if collaborator_name not in org_owners:
                user = {
                    "username": collaborator_name,
                    "permission": highest_permission,
                }

                if collaborator_name in team_members_permissions:
                    # Check if collaborator's permissions differ from team permissions
                    if (
                        highest_permission
                        != team_members_permissions[collaborator_name]
                    ):
                        repo_entry["users"].append(user)
                else:
                    # User is an individual collaborator, not a team member or org owner
                    repo_entry["users"].append(user)
            else:
                print(
                    f"Skipping {collaborator_name} as they are an org owner."
                )

    COLLABORATORS_JSON = "repo-collaborators.json"
    with open(COLLABORATORS_JSON, "w") as f:
        json.dump(all_collaborators_and_teams, f, indent=4)

    print(
        f"\nList of repo collaborators and teams information written to {COLLABORATORS_JSON}\n"
    )


def github_api_request(endpoint: str) -> list:
    """
    Make a request to the GitHub API.
    Handles pagination if there are more than max_results (100).
    """
    http = urllib3.PoolManager()

    all_results = []
    page = 1
    max_results = 100
    params = {"per_page": max_results, "page": page}
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }
    response = http.request(
        "GET",
        f"https://api.github.com{endpoint}",
        fields=params,
        headers=headers,
    )

    # if response.status != 200:
    #     # print("Failed to retrieve data:", response.status)
    #     print(
    #         f"Failed to retrieve data, response code: {response.status} for endpoint: {endpoint}"
    #     )

    data = json.loads(response.data.decode("utf-8"))

    # handle paginated results if there are more than max_results
    if len(data) == max_results:
        all_results.extend(data)
        while len(data) == max_results:
            page += 1
            params = {"per_page": max_results, "page": page}
            response = http.request(
                "GET",
                f"https://api.github.com{endpoint}",
                fields=params,
                headers=headers,
            )
            data = json.loads(response.data.decode("utf-8"))
            all_results.extend(data)
    else:
        return data

    return all_results


if __name__ == "__main__":
    try:
        apikey = os.environ["GITHUB_TOKEN"]
        auth = "Bearer " + apikey
    except KeyError:
        print("GITHUB_TOKEN environment variable not set")
        print("Please set Github API via environment variable.")
        print('Eg: export GITHUB_TOKEN="ghp_XXXXXXXXX"')
        sys.exit(1)

    try:
        org = os.environ["GITHUB_OWNER"]
    except KeyError:
        print("GITHUB_OWNER environment variable not set")
        print("Please set Github Organization via environment variable.")
        print('Eg: export GITHUB_OWNER="google"')
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Please select an option.")
        print(
            f"Usage: {sys.argv[0]} [members|teams|team-membership|repos|repo-collab|branch-protection|all]"
        )
        sys.exit(1)

    if sys.argv[1] == "members":
        get_members()
    elif sys.argv[1] == "teams":
        get_teams()
    elif sys.argv[1] == "team-membership":
        get_team_membership()
    elif sys.argv[1] == "repo-collab":
        get_repo_collaborators()
    elif sys.argv[1] == "repos":
        get_repos()
    elif sys.argv[1] == "branch-protection":
        get_branch_protection()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_membership()
        get_repo_collaborators()
        get_repos()
        get_branch_protection()
