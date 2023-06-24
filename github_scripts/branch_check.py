import os
import sys
import urllib3
import json
import base64


def get_response(url, headers):
    http = urllib3.PoolManager()
    res = http.request("GET", url, headers=headers)
    return json.loads(res.data.decode("utf-8"))


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

headers = {
    "Authorization": "Basic "
    + base64.b64encode((org + ":" + apikey).encode()).decode(),
    "Accept": "application/vnd.github.v3+json",
}

not_protected = []
protected = []
failed_repo = []

# Pagination
page = 1
while True:
    # Step 1: List organization repositories
    repos = get_response(
        f"https://api.github.com/orgs/{org}/repos?page={page}&per_page=100",
        headers,
    )

    # Break loop when no more repos
    if not repos:
        break

    for repo in repos:
        repo_name = repo["name"]
        default_branch = repo["default_branch"]
        archived = repo["archived"]

        # Ignore archived repos
        if archived:
            continue

        # Step 2 and 3: Check if branch protection is applied for each repository
        branch_protection = get_response(
            f"https://api.github.com/repos/{org}/{repo_name}/branches/{default_branch}/protection",
            headers,
        )

        if (
            "message" in branch_protection
            and branch_protection["message"] == "Not Found"
        ):
            print(
                f"No branch protection applied for {repo_name} on branch {default_branch}"
            )
            not_protected.append(repo_name)
        elif "url" in branch_protection:
            print(
                f"Branch protection applied for {repo_name} on branch {default_branch}"
            )
            protected.append(repo_name)
        else:
            print(
                f"Error fetching branch protection for {repo_name} on branch {default_branch}"
            )
            failed_repo.append(repo_name)

    # Go to next page
    page += 1

print()

for repo in not_protected:
    print(f"Not protected: {repo}")
print()
for repo in protected:
    print(f"Protected: {repo}")
print()
for repo in failed_repo:
    print(f"Failed: {repo}")

# Write not_protected list to a file
with open("not_protected.txt", "w") as file:
    file.write("not_protected = " + json.dumps(not_protected, indent=4))

with open("protected.txt", "w") as file:
    file.write("protected = " + json.dumps(protected, indent=4))

with open("failed_repo.txt", "w") as file:
    file.write("failed_repo = " + json.dumps(failed_repo, indent=4))
