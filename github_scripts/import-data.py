import json
import os
import urllib3
import sys


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

    members_output = "members.json"
    with open(members_output, "w") as f:
        json.dump(users_data, f)

    print(f"List of members written to {members_output}\n")


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
