import json
import os
import urllib3
import sys
import pathlib


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


def get_branch_protection():
    """
    Queries all GitHub repositories belonging to a specific organization for
    information and writes the repository information to individual JSON files,
    where each file name is the name of the repository.
    """

    directory_path = pathlib.Path("branch-protection")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)
        print(f'The directory "./{str(directory_path)}" was created.')
    else:
        print(f'The directory "./{str(directory_path)}" already exists.')

    repos = get_organization_repos()

    # for repo in data:
    for repo in repos:
        repo_name = repo["name"]
        file_name = repo_name + ".json"
        full_data_file_name = repo_name + "_full_data.json"

        # Query the /repos/{owner}/{repo} endpoint
        branches = github_api_request(f"/repos/{org}/{repo_name}/branches")

        print()
        print(f"Repo: {repo_name}")
        print()

        for branch in branches:
            branch_name = branch["name"]
            branch_protected = branch["protected"]

            print(
                f"Repo: {repo_name}, Branch: {branch_name}, Protected: {branch_protected}"
            )

            # response = http.request('GET', f'https://api.github.com/repos/{org}/{repo_name}/branches/{branch_name}/protection')
            # protection_data = json.loads(response.data.decode('utf-8'))
            protection_data = github_api_request(
                f"/repos/{org}/{repo_name}/branches/{branch_name}/protection"
            )

            if "required_status_checks" in protection_data:
                required_checks = protection_data["required_status_checks"]
                print(f"Required status checks: {required_checks}")

            if "enforce_admins" in protection_data:
                enforce_admins = protection_data["enforce_admins"]["enabled"]
                print(f"Enforce admins: {enforce_admins}")

            if "required_pull_request_reviews" in protection_data:
                pr_reviews = protection_data["required_pull_request_reviews"]
                print(f"Required pull request reviews: {pr_reviews}")

            if "restrictions" in protection_data:
                restrictions = protection_data["restrictions"]
                print(f"Restrictions: {restrictions}")

            # Write the branch protection data to a JSON file
            data = {
                "repo_name": repo_name,
                "branch_name": branch_name,
                "branch_protected": branch_protected,
                "protection_data": protection_data,
            }
            with open(directory_path / file_name, "w") as file:
                json.dump(data, file, indent=4)

        print("--------------------")

        # below two lines in case you need to view all data from the api
        # with open(f"full_data/{full_data_file_name}", "w") as f:
        # json.dump(repo_data, f, indent=4)

        # Loop through each repository and extract the relevant information
        # for repo in repo_data:
        # repo_info = {
        #     "name": repo_data["name"],
        #     "description": repo_data["description"],
        #     "homepage_url": repo_data["homepage"],
        #     "private": repo_data["private"],
        #     "visibility": repo_data["visibility"],
        #     "has_issues": repo_data["has_issues"],
        #     "has_discussions": repo_data["has_discussions"],
        #     "has_projects": repo_data["has_projects"],
        #     "has_wiki": repo_data["has_wiki"],
        #     "is_template": repo_data["is_template"],
        #     "allow_merge_commit": repo_data["allow_merge_commit"],
        #     "allow_squash_merge": repo_data["allow_squash_merge"],
        #     "allow_rebase_merge": repo_data["allow_rebase_merge"],
        #     "allow_auto_merge": repo_data["allow_auto_merge"],
        #     "squash_merge_commit_title": repo_data[
        #         "squash_merge_commit_title"
        #     ],
        #     "squash_merge_commit_message": repo_data[
        #         "squash_merge_commit_message"
        #     ],
        #     "merge_commit_title": repo_data["merge_commit_title"],
        #     "merge_commit_message": repo_data["merge_commit_message"],
        #     "delete_branch_on_merge": repo_data["delete_branch_on_merge"],
        #     "has_downloads": repo_data["has_downloads"],
        #     # "auto_init": repo_data["auto_init"],
        #     # "gitignore_template": repo_data["gitignore_template"],
        #     # "license_template": repo_data["license_template"],
        #     "default_branch": repo_data["default_branch"],
        #     "archived": repo_data["archived"],
        #     # "archive_on_destroy": repo_data["archive_on_destroy"],
        #     "pages:": repo_data.get("pages", {}),
        #     "security_and_analysis": repo_data.get(
        #         "security_and_analysis", {}
        #     ),
        #     "topics": repo_data.get("topics", []),
        #     # "template": repo_data.get("template", {}),
        #     "vulnerability_alerts": repo_data.get("vulnerability_alerts"),
        #     # "ignore_vulnerability_alerts_during_read": repo_data.get(
        #     # "ignore_vulnerability_alerts_during_read"
        #     # ),
        #     "allow_update_branch": repo_data["allow_update_branch"],
        # }
        # with open(f"{str(directory_path)}/{file_name}", "w") as f:
        #     json.dump(repo_info, f, indent=4)

    print(
        f"\nRepository data is written to the directory ./{directory_path}.\n"
    )


def get_repo_info():
    """
    Queries all GitHub repositories belonging to a specific organization for
    information and writes the repository information to individual JSON files,
    where each file name is the name of the repository.
    """

    directory_path = pathlib.Path("repos")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)
        print(f'The directory "./{str(directory_path)}" was created.')
    else:
        print(f'The directory "./{str(directory_path)}" already exists.')

    repos = get_organization_repos()

    # for repo in data:
    for repo in repos:
        repo_name = repo["name"]
        file_name = repo_name + ".json"
        full_data_file_name = repo_name + "_full_data.json"

        # Query the /repos/{owner}/{repo} endpoint
        repo_data = github_api_request(f"/repos/{org}/{repo_name}")

        # below two lines in case you need to view all data from the api
        # with open(f"full_data/{full_data_file_name}", "w") as f:
        # json.dump(repo_data, f, indent=4)

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
        with open(f"{str(directory_path)}/{file_name}", "w") as f:
            json.dump(repo_info, f, indent=4)

    print(
        f"\nRepository data is written to the directory ./{directory_path}.\n"
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


def get_collaborators_and_teams():
    repos = get_organization_repos()

    all_collaborators_and_teams = {}
    for repo in repos:
        repo_name = repo.get("name")
        collaborators = get_collaborators(repo_name)
        teams = get_collaborators_teams(repo_name)

        repo_entry = all_collaborators_and_teams.setdefault(
            repo_name, {"users": [], "teams": []}
        )

        # Create a dictionary to store team permissions and members
        team_info = {}
        for team in teams:
            permissions = team.get("permissions", {})
            highest_permission = get_highest_permission(permissions)
            members = get_team_members(team.get("name"))
            team_info[team.get("name")] = {
                "permission": highest_permission,
                "members": members,
            }
            repo_entry["teams"].append(
                {
                    "team_id": team.get("name"),
                    "permission": highest_permission,
                }
            )

        for collaborator in collaborators:
            permissions = collaborator.get("permissions", {})
            highest_permission = get_highest_permission(permissions)

            # Check if the collaborator is part of a team
            # and if their permissions differ
            is_in_team = False
            for team, info in team_info.items():
                if collaborator.get("name") in info["members"]:
                    is_in_team = True
                    if highest_permission != info["permission"]:
                        repo_entry["users"].append(
                            {
                                "username": collaborator.get("name"),
                                "permission": highest_permission,
                            }
                        )
                    break

            # If the collaborator is not part of any team,
            # add them to the JSON output
            if not is_in_team:
                repo_entry["users"].append(
                    {
                        "username": collaborator.get("name"),
                        "permission": highest_permission,
                    }
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

    if response.status != 200:
        print("Failed to retrieve data:", response.status)

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
            f"Usage: {sys.argv[0]} [members|teams|team-membership|repos|repo-team-collab|all]"
        )
        sys.exit(1)

    if sys.argv[1] == "members":
        get_members()
    elif sys.argv[1] == "teams":
        get_teams()
    elif sys.argv[1] == "team-membership":
        get_team_membership()
    elif sys.argv[1] == "repos":
        get_repo_info()
    elif sys.argv[1] == "repo-team-collab":
        get_collaborators_and_teams()
    elif sys.argv[1] == "branch-protection":
        get_branch_protection()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_membership()
        get_collaborators_and_teams()
