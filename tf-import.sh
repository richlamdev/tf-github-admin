#!/bin/bash


function import_members() {
  members_file="members.json"

  # Read members from JSON file
  members=$(jq -r '.[] | @base64' $members_file)

  # Loop through members and import state
  for member in $members; do
    decoded_member=$(echo $member | base64 -d)
    username=$(echo $decoded_member | jq -r '.username')

    terraform import "github_membership.member[\"${username}\"]" "${ORG}:${username}"
  done
}


function import_teams() {
  teams_file="teams.json"

  # Parse the JSON file into an array of objects
  teams=$(jq -r '.[] | @base64' $teams_file)

  # Loop through the teams and import the Terraform state for each one
  for team in $teams; do
    decoded_team=$(echo $team | base64 -d)
    team_id=$(echo $decoded_team | jq -r '.id')
    team_slug_name=$(echo $decoded_team | jq -r '.slug')
    #team_name=$(echo $decoded_team | jq -r '.name')

    # use team_slug_name instead of team_name as resource name
    # this allows for easier mass removal of state if required
    terraform import "github_team.teams[\"${team_slug_name}\"]" "${team_id}"
    #terraform import "github_team.teams[\"${team_name}\"]" "${team_id}"
  done
}


function import_team_membership() {
  team_memberships_file="team-membership.json"

  for team_id in $(jq -r '.[].id' team-membership.json); do
    for username in $(jq -r ".[] | select(.id == $team_id) | .members[].username" team-membership.json); do
      terraform import "github_team_membership.team_membership[\"$team_id-$username\"]" "$team_id:$username"
    done
  done
}


function import_repo_collaborators() {
  file="repo-collaborators.json"
  repos=$(jq -r 'keys[]' $file)
  for repo in $repos
  do
      terraform import "github_repository_collaborators.collaborators[\"$repo\"]" $repo
  done
}


function import_repos() {
  for file in repos/*.json
  do
    repo=$(jq -r .name "$file")
    terraform import github_repository.repo[\"$repo\"] "$repo"
  done
}


function import_branch_protection() {
  for file in branch-protection/*.json
  do
    repo=$(jq -r .repository "$file")
    branch=$(jq -r .branch "$file")
    terraform import "github_branch_protection_v3.protection[\"${repo}\"]" "${repo}:${branch}"
  done
}


function main {

  case "$1" in
    members)
      import_members
      ;;
    teams)
      import_teams
      ;;
    team-membership)
      import_team_membership
      ;;
    repo-collab)
      import_repo_collaborators
      ;;
    repos)
      import_repos
      ;;
    branch-protection)
      import_branch_protection
      ;;
    all)
      import_members
      import_teams
      import_team_membership
      import_repo_collaborators
      import_repos
      import_branch_protection
      ;;
    *)
      printf "\n%s" \
        "This script imports Terraform state from a Github Organization" \
        "Designate Github Organization by environment variable GITHUB_ORG" \
        "Eg. export GITHUB_ORG=\"<organization>\"" \
        "" \
        "Usage: $0 [members|teams|team-membership|repos|repo-collab|branch-protection|all]" \
        "" \
        ""
      exit 1
      ;;
  esac

  exit 0
}


GITHUB_TOKEN=${GITHUB_TOKEN:-''}
ORG=${GITHUB_OWNER:-''}

main "$@"

exit 0
