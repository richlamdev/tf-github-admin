import json
import os
import urllib3
import sys
import pathlib


def get_members() -> None:
    """
    Get a list of members in the organization.
    """

    print(f"\nGet all members from {org}.\n")

    all_members = github_api_request(f"/orgs/{org}/members")
    users_array = [user["login"] for user in all_members]

    print("Get organization role for each user.\n")

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

    print(f"List of members written to {MEMBERS_OUTPUT}\n")


def get_teams() -> None:
    """
    Get a list of teams in the organization.
    """

    print(f"\nGet list of teams from {org}.\n")

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

    print(f"\nList of teams written to {TEAM_MEMBERSHIP_JSON}\n")


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

    print(f"\nTeam membership information written to {TEAMS_FOLDER}\n")


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
        print(f"Usage: {sys.argv[0]} [members|teams|team-membership|all]")
        sys.exit(1)

    if sys.argv[1] == "members":
        get_members()
    elif sys.argv[1] == "teams":
        get_teams()
    elif sys.argv[1] == "team-membership":
        get_team_membership()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_membership()
