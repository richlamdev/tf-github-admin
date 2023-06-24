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
    }


def get_team_and_parent():
    if len(sys.argv) > 1:
        team_slug = sys.argv[1]
        team_and_parent = get_team_id_and_parent_slug(team_slug)
        print(
            f"Team ID: {team_and_parent.get('id')}, Parent slug: {team_and_parent.get('parent_slug')}"
        )
    else:
        print("Please provide a team slug as the first argument.")


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

    get_team_and_parent()
