import json
import os
import urllib3
import sys
from pathlib import Path


def get_members():
    print("\n")
    print(f"Get all members from {org}.")
    print("\n")

    http = urllib3.PoolManager()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }

    response = http.request(
        "GET",
        f"https://api.github.com/orgs/{org}/members",
        headers=headers,
    )
    data = json.loads(response.data.decode("utf-8"))

    users_array = [user["login"] for user in data]

    print("Get organization role for each user.\n")

    users_data = []
    for user in users_array:
        response = http.request(
            "GET",
            f"https://api.github.com/orgs/{org}/memberships/{user}",
            headers=headers,
        )
        data = json.loads(response.data.decode("utf-8"))
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

    http = urllib3.PoolManager()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }

    response = http.request(
        "GET",
        f"https://api.github.com/orgs/{org}/teams",
        headers=headers,
    )
    data = json.loads(response.data.decode("utf-8"))

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
    http = urllib3.PoolManager()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"{auth}",
    }
    teams = []

    # Get a list of all teams in the organization
    url = f"https://api.github.com/orgs/{org}/teams"
    response = http.request("GET", url, headers=headers)
    teams_json = json.loads(response.data)
    print(teams_json)
    for team in range(len(teams_json)):
        print()
        teams.append(
            {
                "id": teams_json[team]["id"],
                "name": teams_json[team]["name"],
                "slug": teams_json[team]["slug"],
                "members": [],
            }
        )
    # print(teams[0]["id"])

    # For each team, get a list of its members and their roles
    for team in teams:
        url = f"https://api.github.com/orgs/{org}/teams/{team['slug']}/members"
        response = http.request("GET", url)
        members_json = json.loads(response.data)
        for member in members_json:
            url = f"https://api.github.com/teams/{team['id']}/memberships/{member['login']}"
            response = http.request("GET", url)
            membership_json = json.loads(response.data)
            team_member_role = membership_json["role"]
            team["members"].append(
                {"username": member["login"], "role": team_member_role}
            )

    return json.dumps(teams)


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
        print("Please set the Github API via environment variable.")
        print('Eg: export GITHUB_TOKEN="ghp_XXXXXXXXX"')
        sys.exit(1)

    try:
        org = os.environ["GITHUB_OWNER"]
    except KeyError:
        print("GITHUB_OWNER environment variable not set")
        print("Please set the Github Organization via environment variable.")
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
