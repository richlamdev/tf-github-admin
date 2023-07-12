# tf-github-admin
Managing Github Organization with Terraform


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
resource entries.  (which can be many, many resources depending on the scale of
the platform)  Refer to the Deploy Diagram section.


## How to use / Requirements

1) Knowledge of Terraform and Github Organizations Administration.  (Although,
this is why you've come to this repo!)

2) BASH or ZSH shell.

3) Python 3

4) JQ


Set the environment variables $GITHUB_TOKEN and $GITHUB_OWNER via shell.

IE:

`export GITHUB_ORG="<your organization>"`

`export GITHUB_TOKEN="<your github api token>"`


## Quick Start

`python3 import-data.py members`
`tf-import.sh members`
`terraform state list`
`terraform plan`


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


[github_repository](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository)
[github_repository_collaborators](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborators)
[github_branch_protection_v3](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/branch_protection_v3)


### github_membership implementation

[github_membership](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/membership)

This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all members of the org and their respective
role.  The role is either `member` or `admin`.


### github_team implementation

[github_team](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/team)
This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all teams associated with the org.  Note,
the `create_default_maintainer` parameter is a parameter specific to Terraform,
and not necessarily an option for Github.  This may result in changes to the
Terraform state.  The default in the configuration is `false`.


### github_team_membership implementation

[github_team_membership](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/team_membership)

This is a straight forward data scrape and Terraform importation.  The
API data obtained is a list of all team members of each team.



### github_repository_collaborators implementation

There are two resources to manage Github collaborators via Terraform.

[github_repository_collaborator](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborator)
[github_repository_collaborators](https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_collaborators)

The difference between the two resources, github_repository_collaborator only allows
for adding and removing individual collaborators (users).

The github_repository_collaborators resource allows for the addition
and removal of multiple collaborators (users) and/or teams.

1) Check for all team collaborators associated with a repository.

2) Check for all member collaborators associated with a repository.

3) If a member collaborator is also a member of a team that is collaborator
on the same repo, then compare the permissions of the member vs. the
permissions inherited by the member via the team.  Add this member to the
repository collaborators with the greater set of permissions.

4) If a member collaborator is not a member of a team that is collaborator
on the same repo, however is a individual repository collaborator, then add
the member to the repository collaborators with the permissions assigned.


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
