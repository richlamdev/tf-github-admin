import csv
import json
import os
import urllib3
import sys


def github_api_request(endpoint: str) -> list:
    http = urllib3.PoolManager()
    all_results = []
    page = 1
    max_results = 100
    params = {"per_page": max_results, "page": page}
    headers = {
        "Accept": "application/vnd.github+json",
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
        sys.exit(1)

    data = json.loads(response.data.decode("utf-8"))

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


def get_team_id_and_parent_slug(team_slug: str) -> dict:
    """Get a team's ID and its parent's slug"""
    team_data = github_api_request(f"/orgs/{org}/teams/{team_slug}")
    parent = team_data.get("parent")
    return {
        "name": team_data.get("name"),
        "slug": team_data.get("slug"),
        "id": team_data.get("id"),
        "parent_name": parent.get("name") if parent else None,
        "parent_slug": parent.get("slug") if parent else None,
        "parent_id": parent.get("id") if parent else None,
    }


def get_team_by_name(team_name: str) -> dict:
    """Get a team's detail by its name"""
    teams = github_api_request(f"/orgs/{org}/teams")
    for team in teams:
        if team.get("name").lower() == team_name.lower():
            parent = team.get("parent")
            return {
                "name": team.get("name"),
                "slug": team.get("slug"),
                "id": team.get("id"),
                "parent_name": parent.get("name") if parent else None,
                "parent_slug": parent.get("slug") if parent else None,
                "parent_id": parent.get("id") if parent else None,
            }
    return {}


if __name__ == "__main__":
    try:
        apikey = os.environ["GITHUB_TOKEN"]
        auth = "token " + apikey
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

    if len(sys.argv) > 2:
        option = sys.argv[1]
        parameter = sys.argv[2]
        if option == "-s":
            team_and_parent = get_team_id_and_parent_slug(parameter)
            print(json.dumps(team_and_parent, indent=4))
        elif option == "-n":
            team = get_team_by_name(parameter)
            print(json.dumps(team, indent=4))
        else:
            print(
                "Invalid option. Please provide -s for team slug or -n for team name"
            )
    else:
        print("Please provide an option and parameter.")
