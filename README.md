# Managing Github Organization with Terraform


## Introduction

This repo has two scripts to assist with implementing Terraform to manage
Github Organization(s)


## Terraform Resource Management

The goal of this repo is not only to manage Github Organization(s) via
Terraform, but also manage Terraform resources dynamically.

Due to complexity and/or size of some Github Organizations, statically creating
resources is not feasible.

Terraform is configured to use JSON decode function to dynamically create
resources.  The JSON data becomes the source of truth as opposed to Terraform
resource entries.  (which can be many resources depending on the scale of
the platform)  Refer to the Deploy Diagram section.


## How to use / Requirements

1) Knowledge of Terraform and Github Organizations Administration.  (Although,
this is why you've come to this repo!)

2) BASH or ZSH shell.

3) Python 3

4) [jq](https://stedolan.github.io/jq/)

5) [terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform)


Set the environment variables $GITHUB_TOKEN and $GITHUB_OWNER via shell.

IE:

`export GITHUB_ORG="<your organization>"`\
`export GITHUB_TOKEN="<your github api token>"`


## Quick Start

`source setup-env.sh`\
`python3 import-data.py members`\
`tf-import.sh members`\
`terraform state list`\
`terraform plan`
(alternatively, target plan, with: `terraform plan --target=github_membership.member`)

## import-data.py

This script is located at the root of the repo folder.

import-data.py obtains data from a Github organization via REST API calls
to prepare for mass Terraform importation of present state.

Execute `python3 import-data.py` to view options for data to scrape.
IE: members, teams, team-membership, repos, repo-collaborators, branch-protection

Data output is exported to JSON and is located at the root folder.  The API
data is adjusted for the Terraform resource required/deployed.  The
tf-import.sh script handles the mass Terraform state import.
Refer following section for more information for Terraform importation.


## tf-import.sh

This script is located at the root of the repo folder.

tf-import.sh sets up the Terraform resources to enable mass importation of state.

Execute ./tf-import.sh to view options for Terraform importation.
IE: members, teams, team-membership, repos, repo-collaborators, branch-protection

Monitor the output during execution of this script for potential errors.

After importation is done, check the Terraform state to verify proper
importation.

`terraform state list` followed by

`terraform plan`

Theoretically, zero (0) changes should be applied against the Github
Organization in which the data imported from.  Importing repo-collaborators and
branch-protection may result in some changes observed from the the terraform
plan output. (see below for more information regarding potential changes)

Note, with the release of [Terraform v1.5](https://www.hashicorp.com/blog/terraform-1-5-brings-config-driven-import-and-checks),
this method is likely no longer required.  Terraform v1.5 has improved
support for Terraform importation.


## Terraform Resources

#### [github_membership](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/membership)

`python3 import-data.py members`\
`tf-import.sh members`


This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all members of the org and their respective
role.  The role is either `member` or `admin`.


#### [github_team](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/team)

`python3 import-data.py teams`\
`tf-import.sh teams`

This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all teams associated with the org.  Note,
the `create_default_maintainer` parameter is a parameter specific to Terraform,
and not necessarily an option for Github.  This may result in changes to the
Terraform state.  The default in the configuration is `false`.


#### [github_team_membership](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/team_membership)

`python3 import-data.py team-membership`\
`tf-import.sh team-membership`

This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all team members of each team, with their
respective role.


#### [github_repository](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository)

`python3 import-data.py repos`\
`tf-import.sh repos`


This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all repos associated with the org.

The JSON data used for the importation for all the repositories are
stored as individual files in the `repos/` folder at the root of the repo.
Storing as separate files due was chosen due to potential long length
of a single file of all repos.  This allows for easier management, when
amending changes to a repo.

There is an additional folder `repos-full-data` created, with the execution of
`python3 import-data.py repos`  This folder contains the full api data of each
repository.  This is for reference if needed.  For the most part, this folder
can be ignored


#### [github_repository_collaborators](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborators)

`python3 import-data.py repo-collab`\
`tf-import.sh repo-collab`

There are two resources to manage Github collaborators via Terraform:

[github_repository_collaborator](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborator) and
[github_repository_collaborators](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborators)

The difference between the two resources, github_repository_collaborator only allows
for adding and removing individual collaborators (users).

The github_repository_collaborators resource allows for the addition
and removal of multiple collaborators (users) and/or teams.  As a result the
github_repository_collaborators resource was chosen to minimize the number
of state resource entries created for each repository.

The logic/workflow for creating the JSON data for this resource is as follows:

1) Obtain all Github organization owners.

2) Obtain all member collaborators associated with a repository.

3) Obtain all team collaborators associated with a repository.

4) Do not add Github organization owners to the repository collaborators list.
(this is already default, but does not appear on the via Github UI).

5) If a member collaborator is also a member of a team that is collaborator
on the same repo, then compare the permissions of the member vs. the
permissions inherited by the member via the team.  Add this member to the
repository collaborators if the permissions differ.

6) If a member collaborator is not a member of a team that is collaborator
on the same repo, however is a individual repository collaborator, then add
the member to the repository collaborators list with the permissions assigned.

Note, after executing `terraform plan` or
`terraform plan --target=github_repository_collaborators.collaborators`
it is likely the output will have several changes/in-place updates.
This is due to a slight error in the process above described.  Due to slight
discrepancies in the users list you may notice minor potential changes
Github UI.  In most cases there may be added users; added users that are
already collaborators via team membership.  However, in some cases there
may be removed users; removed users that are not collaborators via team
membership.  This is a known bug, that needs to be corrected.


#### [github_branch_protection_v3](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/branch_protection_v3)

`python3 import-data.py branch-protection`\
`tf-import.sh branch-protection`

Current branch protection data is obtained for the default branch of each
repository.  In the event branch protection is not enabled for a repository,
the default JSON data defaults to the following minimal configuration:

`enforce_admins: true`\
`required_approving_review_count: 1`\
`required_status_checks: true`

The above minimal configuration will be applied to the default branch of any
repository that does not have branch protection configured.  (If branch protection
is configured, the configuration will not be changed)

There is an additional folder `branch-protection-full-data/` created, with the
execution of `python3 import-data.py branch-protection`  This folder contains
the full branch protection api data of each repository.  This is for reference
if needed.  For the most part, this folder can be ignored.

Notes:

1) The `apps` list for the bypass_pull_request_allowances or restrictions
block is not implemented.

2) The `contexts` for the required_status_checks block is omitted, as it is a
deprecated value per HashiCorp documentation.

3) Review the JSON data and/or `import-data.py` to ensure that the
configuration is correct for your organization.  This resource has a number of
options that may need to be adjusted.


## Manage Configuration Changes Post Terraform State Import


After each edit(s)in the below steps, execute `terraform plan` and
`terraform apply`


#### Add / remove member to to the organization

Edit the members.json file


#### Add / remove team to the organization

Edit the teams.json file

When adding/creating a team via editing teams.json, the `id` value is not
required in the teams.json, populate the `id` value as `null` temporarily.
The same applies for `parent_team_id` and `slug` values.

The `id` value is required when amending team membership.


#### Add / remove team-membership to the organization

Edit the team-membership.json file.  As mentioned above, the `id` value is
required for team-membership.  At present, the `id` value can only be obtained
via the API.

Use the script/command `python3 ./scripts/get-team-id.py "team name"` to obtain
the `id` value.  The parameter accepts either a team or slug name.  The value
is returned via STDOUT.  Enter this value into the team-membership.json file.

This is not an ideal workflow, however, it is an interim solution until a value
is obatained/passed directly from Terraform State.


#### Add / remove a repository to the organization

Copy one of the repository files in the `repos/` folder as the name of the
target repository.  Naturally, change the "name" field to the name of the
repository, and optionally edit any other fields as needed.


#### Add / remove a repository collaborator to the organization

Edit the repo-collaborators.json file.  Add or remove individual
collaborator(s) and/or team(s) to repository entries as needed.  It is
recommended to add/remove teams only to simplify administration.
Of course, that requires collaborators to be added to teams as needed.


#### Add / remove a branch protection to repositories

Copy one of the repository files in the `branch-protection/` folder as the name
of the target repository.  Edit the "repository" and "branch" fields, as well
as other fields as needed.


## Deployment Diagram


     ┌──────────────────────────────────┐
     │                                  │
     │   Initial Setup/Deployment       │
     │                                  │
     │                                  │
     │   ┌──────────────┐               │                          ┌──────────┐
     │   │              │               │    ┌─────┐               │          │
     │   │ Github       │ import-data.py│    │     │ tf-import.sh  │Terraform │
     │   │ Organization ├───────────────┼───►│JSON ├──────────────►│State     │
     │   │ (Current     │               │    │Data │               │(local or │
     │   │  State)      │               │    │     │               │ cloud)   │
     │   │              │               │    └─────┘               └──────────┘
     │   └──────────────┘               │       ▲
     │                                  │       │
     └──────────────────────────────────┘       │
                                                │
                                                │
                                 ┌──────────────┼──────────────────┐
                                 │              │                  │
                                 │              ▼                  │
                                 │     ┌─────────────────────┐     │
                                 │     │ Create / Modify     │     │
                                 │     │ Github Organization │     │
                                 │     │ Settings via Pull   │     │
                                 │     │ Request             │     │
                                 │     └─────────────────────┘     │
                                 │                                 │
                                 │       Ongoing Deployment        │
                                 │                                 │
                                 │                                 │
                                 │                                 │
                                 └─────────────────────────────────┘

## ToDo

-add information for `scripts/` folder

-document decisions made / implementation
