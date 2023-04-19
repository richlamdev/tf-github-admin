# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

provider "github" {

  #token = "<GITHUB_TOKEN>"
  #owner = "<GITHUB_OWNER>"

  # read GITHUB_TOKEN from environment variable
  # export GITHUB_TOKEN
  #
  # read GITHUB_OWNER from environment variable
  # export GITHUB_OWNER
}


# Retrieve information about the currently (PAT) authenticated user
#data "github_user" "self" {
#username = ""
#}
