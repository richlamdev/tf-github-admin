import os
import sys
import urllib3
import json
import base64

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
    'Authorization': 'Basic ' + base64.b64encode((org+":"+apikey).encode()).decode(),
    'Accept': 'application/vnd.github.v3+json'
}

http = urllib3.PoolManager()

# List organization repositories
repos_res = http.request('GET', f'https://api.github.com/orgs/{org}/repos', headers=headers)
repos = json.loads(repos_res.data.decode('utf-8'))

not_protected = []
protected = []
failed_repo = []

for repo in repos:
    repo_name = repo['name']
    default_branch = repo['default_branch']

    # Check if branch protection is applied for each repository
    branch_protection_res = http.request('GET', f'https://api.github.com/repos/{org}/{repo_name}/branches/{default_branch}/protection', headers=headers)

    if branch_protection_res.status == 404:
        print(f'No branch protection applied for {repo_name} on branch {default_branch}')
        not_protected.append(repo_name)
    elif branch_protection_res.status == 200:
        print(f'Branch protection applied for {repo_name} on branch {default_branch}')
        protected.append(repo_name)
    else:
        print(f'Error fetching branch protection for {repo_name} on branch {default_branch}')
        failed_repo.append(repo_name)

print()

for repo in not_protected:
    print(f"Not protected: {repo}")

# Write not_protected list to a file
with open('not_protected.txt', 'w') as file:
    file.write('not_protected = ' + json.dumps(not_protected, indent=4))
