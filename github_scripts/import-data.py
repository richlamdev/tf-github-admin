import json
import os
import urllib3
import sys


def get_members():
    print(f"\nGet all members from {org}.\n")

    data = github_api_request(f"/orgs/{org}/members")

    users_array = [user["login"] for user in data]

    print("Get organization role for each user.\n")

    users_data = []
    for user in users_array:
        data = github_api_request(f"/orgs/{org}/memberships/{user}")
        user_data = {"username": data["user"]["login"], "role": data["role"]}
        users_data.append(user_data)

    MEMBERS_OUTPUT = "members.json"
    with open(MEMBERS_OUTPUT, "w") as f:
        json.dump(users_data, f)

    print(f"List of members written to {MEMBERS_OUTPUT}\n")


def get_teams():
    print(f"\nGet list of teams from {org}.\n")

    TEAMS_JSON = "teams.json"
    with open(TEAMS_JSON, "w") as f:
        f.write("name,id,description,privacy,parent_team_id,slug\n")

    data = github_api_request(f"/orgs/{org}/teams")

    teams_data = []
    for team in range(len(data)):
        name = data[team]["name"]
        team_id = data[team]["id"]
        description = (
            data[team]["description"] if data[team]["description"] else "null"
        )
        privacy = data[team]["privacy"]
        parent_team_id = (
            data[team]["parent"]["id"] if data[team]["parent"] else "null"
        )
        slug = data[team]["slug"]

        team_data = {
            "name": name,
            "id": team_id,
            "description": description,
            "privacy": privacy,
            "parent_team_id": parent_team_id,
            "slug": slug,
        }

        teams_data.append(team_data)

    with open(TEAMS_JSON, "w") as f:
        json.dump(teams_data, f)

    print(f"\nList of teams written to {TEAMS_JSON}\n")


def get_team_memberships():

    teams_json = github_api_request(f"/orgs/{org}/teams")

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

    # For each team, get a list of its members and their roles
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
        json.dump(teams, f)

    print(f"\nList of teams written to {TEAM_MEMBERSHIP_JSON}\n")


def github_api_request(endpoint):
    http = urllib3.PoolManager()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }
    response = http.request(
        "GET",
        f"https://api.github.com{endpoint}",
        headers=headers,
    )
    return json.loads(response.data.decode("utf-8"))


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
        get_team_memberships()
    elif sys.argv[1] == "all":
        get_members()
        get_teams()
        get_team_memberships()
