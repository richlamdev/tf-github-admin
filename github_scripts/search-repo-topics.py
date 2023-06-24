import argparse
import json

# import pathlib
import os
import sys
import urllib3


def get_repos(search_topic: str) -> None:
    """
    Queries all GitHub repositories belonging to a specific organization for
    information and writes the repository information to individual JSON files,
    where each file name is the name of the repository. Returns a list of repositories
    that contain the specified topic.
    """

    # full_data_dir_path = pathlib.Path("repos-full-data")
    # if not full_data_dir_path.exists():
    #     full_data_dir_path.mkdir(parents=True)
    #     print(f'The directory "./{str(full_data_dir_path)}" was created.')
    # else:
    #     print(f'The directory "./{str(full_data_dir_path)}" already exists.')

    repos = get_organization_repos(search_topic)

    matching_repos = []

    for repo in repos:
        repo_name = repo["name"]
        # full_data_file_name = repo_name + "_full_data.json"

        # Query the /repos/{owner}/{repo} endpoint
        repo_data = github_api_request(f"/repos/{org}/{repo_name}")

        # with open(f"{full_data_dir_path}/{full_data_file_name}", "w") as f:
        #     json.dump(repo_data, f, indent=4)

        if search_topic in repo_data.get("topics", []):
            matching_repos.append(repo_name)

    # print(f"Repository full API data is written to the directory ./{full_data_dir_path}.\n")
    # print(f"\nRepositories matching topic '{search_topic}':\n")

    matched_repos = "matching_repos.txt"
    print(f"\nRepositories matching topic '{search_topic}':\n")
    with open(f"{matched_repos}", "w") as f:
        for repo in matching_repos:
            print(repo)
            f.write(repo + "\n")
    print()

    print(f"List of matching repos written to {matched_repos}")


def get_organization_repos(search_topic: str):
    # Get all repos from the organization
    all_repos = github_api_request(f"/orgs/{org}/repos")

    # Filter only non-archived repos
    non_archived_repos = [
        repo for repo in all_repos if not repo.get("archived", False)
    ]

    return non_archived_repos


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

    parser = argparse.ArgumentParser(
        description="Search topic in GitHub repos"
    )
    parser.add_argument("topic", type=str, help="Topic to search for")

    args = parser.parse_args()
    get_repos(args.topic)
