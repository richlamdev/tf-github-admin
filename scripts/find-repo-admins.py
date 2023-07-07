import csv
import json
import os
import urllib3
import sys


def get_organization_repos():
    all_repos = github_api_request(f"/orgs/{org}/repos")
    non_archived_repos = [
        repo for repo in all_repos if not repo.get("archived", False)
    ]
    return non_archived_repos


def get_organization_owners():
    all_members = github_api_request(f"/orgs/{org}/members")
    owners = []
    for member in all_members:
        username = member.get("login")
        user_membership = github_api_request(
            f"/orgs/{org}/memberships/{username}"
        )
        if user_membership.get("role") == "admin":
            owners.append(username)
    return owners


def get_collaborators(repo_name):
    collaborators_data = github_api_request(
        f"/repos/{org}/{repo_name}/collaborators"
    )
    collaborators = []
    for data in collaborators_data:
        if data.get("permissions", {}).get("admin", False):
            collaborators.append(data.get("login"))
    return collaborators


def get_teams_with_access(repo_name):
    teams_data = github_api_request(f"/repos/{org}/{repo_name}/teams")
    teams = []
    for data in teams_data:
        if data.get("permissions", {}).get("admin", False):
            teams.append(data.get("name"))
    return teams


def get_team_members(team_slug):
    team_members_data = github_api_request(
        f"/orgs/{org}/teams/{team_slug}/members"
    )
    team_members = [data.get("login") for data in team_members_data]
    return team_members


def find_repos_with_admins():
    repos = get_organization_repos()
    org_owners = get_organization_owners()
    repos_with_admins = []

    for repo in repos:
        repo_name = repo.get("name")
        collaborators = get_collaborators(repo_name)
        teams = get_teams_with_access(repo_name)

        team_members = []
        for team in teams:
            team_slug = team.replace(" ", "-").lower()
            team_members.extend(get_team_members(team_slug))

        individual_admins = [
            collab
            for collab in collaborators
            if collab not in org_owners and collab not in team_members
        ]

        if individual_admins or teams:
            repos_with_admins.append(
                [repo_name, ", ".join(individual_admins), ", ".join(teams)]
            )

    # Write data to CSV file
    with open("repos_and_admins.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Repo", "Admins", "Teams"])
        writer.writerows(repos_with_admins)


# def find_repos_with_admins():
#     repos = get_organization_repos()
#     org_owners = get_organization_owners()
#     repos_with_admins = []

#     for repo in repos:
#         repo_name = repo.get("name")
#         collaborators = get_collaborators(repo_name)
#         teams = get_teams_with_access(repo_name)

#         collaborators = [
#             collab for collab in collaborators if collab not in org_owners
#         ]

#         if collaborators or teams:
#             repos_with_admins.append(
#                 [repo_name, ", ".join(collaborators), ", ".join(teams)]
#             )

#     # Write data to CSV file
#     with open("repos_and_admins.csv", "w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["Repo", "Admins", "Teams"])
#         writer.writerows(repos_with_admins)


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

    find_repos_with_admins()
