# tf-github-admin
Managing Github Organization with Terraform


## Introduction

This repo has two scripts to assist with implementing Terraform to manage
Github Organization(s)


## How to use / Requirements

1) Knowledge of Terraform and Github Organizations Administration.  (Although,
this is why you've come to this repo - likely familar with the aformentioned)

2) BASH shell.  ToDo, write it for compatibility with ZSH.

3) Ensure [Github CLI](https://cli.github.com/) (gh) is installed.


Set the environment variables $GITHUB_TOKEN and $GITHUB_OWNER via shell.

IE:

export GITHUB_ORG="<your organization>"

export GITHUB_TOKEN="<your github api token>"


## import-data.sh

This script is located in github_scripts/. This is subject (likely) to move to i
the root folder.

import-data.sh scrapes from a Github organization to prepare for mass Terraform
importation of present state deployed state.

Execute ./import-data.sh to view options for data to scrape.
IE: memberships,teams, team-memberships, repositories, respository options etc.

Data output is exported to CSV and is located at the root folder.  This data
is used by tf-import.sh for Terraform import.  See following section.


## tf-import.sh

This script is located at the root of the repo folder.

tf-import.sh sets up the Terraform resources to enable mass importation of state.

Execute ./tf-import.sh to view options for Terraform importation.
IE: memberships,teams, team-memberships, repositories, respository options etc.

Monitor the output during execution of this script for potential errors.

After importation is done, check the Terraform state to verify proper
importation.

`Terraform state list` followed by

`Terraform plan`

Theoretically, zero (0) changes should be applied against the Github
Organization in which the data imported from.
