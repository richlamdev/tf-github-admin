import json
import os
import urllib3
import sys
import pathlib


def get_members_old():
    """
    Get a list of members in the organization.
    Pagination is handled.
    """

    print(f"\nGet all members from {org}.\n")

    all_members = []
    page = 1
    max_results = 100
    query_params = {"per_page": max_results, "page": page}

    data = github_api_request_new(f"/orgs/{org}/members", query_params)
    all_members.extend(data)

    # Query all results if there are more than 100 members
    if len(data) == max_results:
        while len(data) == max_results:
            page += 1
            query_params = {"per_page": max_results, "page": page}
            data = github_api_request_new(f"/orgs/{org}/members", query_params)
            all_members.extend(data)

    #    all_members = github_api_request("/orgs/{org}/members")

    users_array = [user["login"] for user in all_members]

    print("Get organization role for each user.\n")

    page = 1

    # Get the role of each user in the organization.
    users_data = []
    for user in users_array:
        data = github_api_request_new(
            f"/orgs/{org}/memberships/{user}", query_params
        )
        user_data = {"username": data["user"]["login"], "role": data["role"]}
        users_data.append(user_data)

    MEMBERS_OUTPUT = "members.json"
    with open(MEMBERS_OUTPUT, "w") as f:
        json.dump(users_data, f, indent=4)

    print(f"List of members written to {MEMBERS_OUTPUT}\n")


def get_members_new():
    """
    Get a list of members in the organization.
    Pagination is handled.
    """

    print(f"\nGet all members from {org}.\n")

    all_members = []
    page = 1
    max_results = 100
    query_params = {"per_page": max_results, "page": page}
    #
    #    data = github_api_request_new(f"/orgs/{org}/members", query_params)
    #    all_members.extend(data)
    #
    #    # Query all results if there are more than 100 members
    #    if len(data) == max_results:
    #        while len(data) == max_results:
    #            page += 1
    #            query_params = {"per_page": max_results, "page": page}
    #            data = github_api_request_new(f"/orgs/{org}/members", query_params)
    #            all_members.extend(data)
    #
    all_members = github_api_request(f"/orgs/{org}/members")
    users_array = [user["login"] for user in all_members]

    print("Get organization role for each user.\n")

    # Get the role of each user in the organization.
    users_data = []
    for user in users_array:

        print()
        print(user)
        print()
        data = github_api_request(f"/orgs/{org}/memberships/{user}")

        print(data)

        # data = github_api_request_new(
        # f"/orgs/{org}/memberships/{user}", query_params
        # )
        user_data = {"username": data["user"]["login"], "role": data["role"]}
        users_data.append(user_data)

    MEMBERS_OUTPUT = "members.json"
    with open(MEMBERS_OUTPUT, "w") as f:
        json.dump(users_data, f, indent=4)

    print(f"List of members written to {MEMBERS_OUTPUT}\n")


def get_teams():
    """
    Get a list of teams in the organization.
    Does not handle pagination yet.
    """

    print(f"\nGet list of teams from {org}.\n")

    page = 1
    max_results = 100
    query_params = {"per_page": max_results, "page": page}

    data = github_api_request_new(f"/orgs/{org}/teams", query_params)

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

        # schema for the JSON
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


def get_team_memberships_old():
    """
    Get a list of teams in the organization and their members and roles.
    Writes to a single JSON file, indicated by TEAMS_MEMBERSHIP_JSON.
    Does not handle pagination yet.
    """

    page = 1
    max_results = 100
    query_params = {"per_page": max_results, "page": page}
    teams_json = github_api_request_new(f"/orgs/{org}/teams", query_params)

    # schema for the JSON
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
        members_json = github_api_request_new(
            f"/orgs/{org}/teams/{team['slug']}/members", query_params
        )
        # For each member, get their role in the team
        for member in members_json:
            membership_json = github_api_request_new(
                f"/teams/{team['id']}/memberships/{member['login']}",
                query_params,
            )
            team_member_role = membership_json["role"]
            team["members"].append(
                {"username": member["login"], "role": team_member_role}
            )

    TEAM_MEMBERSHIP_JSON = "team_memberships.json"
    with open(TEAM_MEMBERSHIP_JSON, "w") as f:
        json.dump(teams, f, indent=4)

    print(f"\nList of teams written to {TEAM_MEMBERSHIP_JSON}\n")


def get_team_memberships():
    """
    Get a list of teams in the organization and their members and roles.
    Writes team data to individual JSON files and stored in TEAMS_FOLDER.
    Does not handle pagination yet.
    """

    page = 1
    max_results = 100
    query_params = {"per_page": max_results, "page": page}

    TEAMS_FOLDER = "team-memberships/"

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

    teams_json = github_api_request_new(f"/orgs/{org}/teams", query_params)

    # schema for the JSON
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
        members_json = github_api_request_new(
            f"/orgs/{org}/teams/{team['slug']}/members", query_params
        )
        # For each member, get their role in the team
        for member in members_json:
            membership_json = github_api_request_new(
                f"/teams/{team['id']}/memberships/{member['login']}",
                query_params,
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


def github_api_request_new(endpoint: str, query_params: dict = None) -> list:
    http = urllib3.PoolManager()
    query_params = query_params if query_params else {}
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }
    response = http.request(
        "GET",
        f"https://api.github.com{endpoint}",
        fields=query_params,
        headers=headers,
    )

    return json.loads(response.data.decode("utf-8"))


def github_api_request(endpoint):
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
    all_results.extend(data)

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
        get_members_new()
    elif sys.argv[1] == "teams":
        get_teams()
    elif sys.argv[1] == "team-membership":
        get_team_memberships_old()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_memberships()
