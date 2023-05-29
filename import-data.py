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

    TEAM_MEMBERSHIP_JSON = "team_memberships.json"
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


def write_repo_info_to_file(repo_info, file_path):
    """
    Writes repository information to a JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(repo_info, f)


def get_repo_info():
    """
    Queries all GitHub repositories belonging to a specific organization for information
    and writes the repository information to individual JSON files, where each file name
    is the name of the repository.
    """
    # Create a urllib3 PoolManager instance
    # http = urllib3.PoolManager()

    # Construct the API request URL
    # url = f"https://api.github.com/orgs/{org}/repos"

    # Add headers to the request to authenticate with the GitHub API
    # headers = {
    # "User-Agent": "python",
    # "Authorization": "token YOUR_GITHUB_TOKEN",
    # }

    # Send the GET request to the GitHub API and parse the JSON response
    # response = http.request("GET", url, headers=headers)
    # data = json.loads(response.data.decode("utf-8"))
    # data = github_api_request(f"/orgs/{org}/repos")
    data = github_api_request(f"/orgs/{org}/repos")

    repo_name = []
    branch_name = []

    for repo in data:
        file_name = repo["name"] + ".json"
        file_path = f"./repos/{file_name}"
        with open(file_path, "w") as f:
            json.dump(repo, f, indent=4)

        repo_name.append(repo["name"])
        branch_name.append(repo["default_branch"])

    for repo, branch in zip(repo_name, branch_name):
        print(repo)
        data = github_api_request(
            f"/repos/{org}/{repo}/branches/{branch}/protection"
        )

        file_name = f"{repo}-{branch}-protection" + ".json"
        file_path = f"./repos/{file_name}"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    # write_repo_info_to_file(repo, file_path)


#    # Loop through each repository and extract the relevant information
#    for repo in data:
#        repo_info = {
#            "name": repo["name"],
#            "description": repo["description"],
#            "homepage_url": repo["homepage"],
#            "private": repo["private"],
#            "has_issues": repo["has_issues"],
#            "has_wiki": repo["has_wiki"],
#            "has_projects": repo["has_projects"],
#            # "allow_merge_commit": repo["allow_merge_commit"],
#            # "allow_squash_merge": repo["allow_squash_merge"],
#            # "allow_rebase_merge": repo["allow_rebase_merge"],
#            # "delete_branch_on_merge": repo["delete_branch_on_merge"],
#            "archived": repo["archived"],
#        }
#
#        # Write the repository information to a JSON file
#        file_name = repo_info["name"] + ".json"
#        file_path = f"./repos/{file_name}"
#        write_repo_info_to_file(repo_info, file_path)


# def get_github_data(org_name, personal_access_token):
def get_collaborators():

    repos = github_api_request(f"/orgs/{org}/repos")

    collaborators = []
    # Weights for the permissions
    permission_weights = {
        "admin": 5,
        "maintain": 4,
        "push": 3,
        "triage": 2,
        "pull": 1,
    }

    # Loop through all repos
    for repo in repos:
        # Endpoint to get all collaborators in a repo
        collabs = github_api_request(
            f"/repos/{org}/{repo['name']}/collaborators"
        )

        # Loop through all collaborators
        for collab in collabs:
            permissions = collab["permissions"]

            max_permission = max(
                (perm for perm, has_perm in permissions.items() if has_perm),
                key=permission_weights.get,
            )

            # JSON schema
            collaborators.append(
                {
                    "repo": repo["name"],
                    "user": collab["login"],
                    "permission": max_permission,
                }
            )

    COLLABORATORS_JSON = "repo-collaborators.json"
    with open(COLLABORATORS_JSON, "w") as f:
        json.dump(collaborators, f, indent=4)

    print(
        f"\nList of repo collaborators information written to {COLLABORATORS_JSON}\n"
    )


# Define a dictionary to store permissions
permissions_priority = {
    "read": 1,
    "write": 2,
    "admin": 3,
}


permissions_priority = {"read": 1, "write": 2, "admin": 3}


def get_all_collaborators():
    teams_and_members = get_teams_with_members()
    repos_data = github_api_request(f"/orgs/{org}/repos")
    repositories = [
        repo["full_name"] for repo in repos_data if not repo["archived"]
    ]

    collaborator_permissions = {}  # Dictionary to track highest permissions

    repo_collaborators = (
        {}
    )  # Dictionary to hold all collaborators for each repository

    for repo in repositories:
        owner, repo_name = repo.split("/")

        members_data = github_api_request(
            f"/repos/{owner}/{repo_name}/collaborators"
        )
        member_names = [member["login"] for member in members_data]

        print(f"Repository: {owner}/{repo_name}")
        print("Members collaborating on the repository:")

        # List to hold collaborators for this repository
        collaborators = []
        for member in member_names:
            print(member)

            # Get the member permissions
            member_permissions = get_member_permissions(member, repo)

            # If this member has been found before, compare the permissions
            if member in collaborator_permissions:
                if (
                    permissions_priority[member_permissions]
                    > permissions_priority[collaborator_permissions[member]]
                ):
                    # Update permission in collaborator_permissions dictionary
                    collaborator_permissions[member] = member_permissions
            else:
                # Add this member to the collaborator_permissions dictionary
                collaborator_permissions[member] = member_permissions

            collaborator = {
                "username": member,
                "permissions": collaborator_permissions[member],
            }

            # Add this collaborator to the collaborators list
            collaborators.append(collaborator)

        # Add the collaborators list to the repo_collaborators dictionary
        repo_collaborators[repo_name] = collaborators

    # Save repo_collaborators to a JSON file
    with open("individual_collaborators.json", "w") as file:
        json.dump(repo_collaborators, file, indent=4)

    return collaborator_permissions


def get_member_permissions(username, repo):
    """Get member permissions for a repository."""
    permission_data = github_api_request(
        f"/repos/{repo}/collaborators/{username}/permission"
    )

    user_permissions = permission_data["user"]["permissions"]
    # Assuming "read" < "write" < "maintain" < "triage" < "admin"
    permissions_priority = {
        "pull": 1,
        "push": 2,
        "maintain": 3,
        "triage": 4,
        "admin": 5,
    }
    highest_permission = max(
        user_permissions, key=lambda p: permissions_priority[p]
    )

    return highest_permission


def get_team_permissions(team_name, repo):
    teams_data = github_api_request(f"/repos/{repo}/teams")
    for team in teams_data:
        if team["name"] == team_name:
            return team["permission"]
    return None


def compare_permissions(
    member, member_permissions, team_name, team_permissions
):
    if member_permissions is None or team_permissions is None:
        return

    print(f"Comparing permissions for {member} in team {team_name}")
    print(f"Member permissions: {member_permissions}")
    print(f"Team permissions: {team_permissions}")

    if member_permissions == team_permissions:
        print("Member and team have the same level of permission.")
    elif member_permissions == "admin":
        print("Member has greater privilege than the team.")
        return "member_has_more_privilege"  # Return a string when member has more privilege
    elif team_permissions == "admin":
        print("Team has greater privilege than the member.")
    else:
        print(
            "Member and team have different levels of permission, but neither has greater privilege."
        )
    print()


def get_teams_with_members():

    teams_data = github_api_request(f"/orgs/{org}/teams")

    teams_with_members = {}

    # Iterate through each team
    for team in teams_data:
        team_name = team["name"]
        team_members_data = github_api_request(f"/teams/{team['id']}/members")

        # Add team members to the team
        team_members = []
        for team_member in team_members_data:
            team_members.append(team_member["login"])

        teams_with_members[team_name] = team_members

    return teams_with_members


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
            f"Usage: {sys.argv[0]} [members|teams|team-membership|repos|repo-collab|repo-team-collab|all]"
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
    elif sys.argv[1] == "repo-collab":
        get_collaborators()
    elif sys.argv[1] == "repo-team-collab":
        get_all_collaborators()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_membership()
        get_collaborators()
