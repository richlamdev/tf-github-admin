# tf-github-admin
Managing Github Organization with Terraform


## Introduction

This repo has two scripts to assist with implementing Terraform to manage
Github Organization(s)


## Terraform Resource Management

The goal of this repo is not only to manage Github Organization(s) via
Terraform, but to manage Terraform resources in a dynamic manner.

Due to the complexity and/or size of Github Organizations, statically creating
resources is not feasible.

Using JSON data, Terraform utilizes the internal JSON decode function to
dynamically create resources.  As a result of using JSON data, the creation of
resources is controlled via a JSON source file as opposed to Terraform resource
entries.  (which can be many, many resources depending on the scale of the
platform)  Refer to the Deploy Diagram section.


## How to use / Requirements

1) Knowledge of Terraform and Github Organizations Administration.  (Although,
this is why you've come to this repo!)

2) BASH or ZSH shell.

3) Python 3

4) JQ


Set the environment variables $GITHUB_TOKEN and $GITHUB_OWNER via shell.

IE:

export GITHUB_ORG="<your organization>"

export GITHUB_TOKEN="<your github api token>"


## import-data.py

This script is located at the root of the repo folder.

import-data.py scrapes from a Github organization to prepare for mass Terraform
importation of present state deployed state.

Execute python3 import-data.py to view options for data to scrape.
IE: members, teams, team-membership, repositories, respository options etc.

Data output is exported to JSON and is located at the root folder.  This data
is used by tf-import.sh for Terraform import.  See following section.


## tf-import.sh

This script is located at the root of the repo folder.

tf-import.sh sets up the Terraform resources to enable mass importation of state.

Execute ./tf-import.sh to view options for Terraform importation.
IE: members, teams, team-membership, repositories, respository options etc.

Monitor the output during execution of this script for potential errors.

After importation is done, check the Terraform state to verify proper
importation.

`Terraform state list` followed by

`Terraform plan`

Theoretically, zero (0) changes should be applied against the Github
Organization in which the data imported from.


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
