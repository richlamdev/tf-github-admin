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
        "id": team_data.get("id"),
        "parent_slug": parent.get("slug") if parent else None,
        "parent_id": parent.get("id") if parent else None,
    }


def get_team_by_id(team_id: str) -> dict:
    """Get a team's detail by its ID"""
    teams = github_api_request(f"/orgs/{org}/teams")
    for team in teams:
        if team.get("id") == int(team_id):
            return team
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
            print(
                f"Team ID: {team_and_parent.get('id')}, Parent Team ID: {team_and_parent.get('parent_id')}, Parent Team Slug: {team_and_parent.get('parent_slug')}"
            )
        elif option == "-t":
            team = get_team_by_id(parameter)
            print(f"Team: {team}")
        else:
            print(
                "Invalid option. Please provide -s for team slug or -t for team id."
            )
    else:
        print("Please provide an option and parameter.")
