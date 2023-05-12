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
    team_name=$(echo $decoded_team | jq -r '.name')

    terraform import "github_team.teams[\"${team_name}\"]" "${team_id}"
  done
}


function import_team_membership() {
  team_memberships_file="team_memberships.json"

  for team_id in $(jq -r '.[].id' team_memberships.json); do
    for username in $(jq -r ".[] | select(.id == $team_id) | .members[].username" team_memberships.json); do
      terraform import "github_team_membership.team_memberships[\"$team_id-$username\"]" "$team_id:$username"
    done
  done
}

function test() {
  terraform init
  terraform plan
  terraform apply
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
    all)
      import_members
      import_teams
      import_team_membership
      ;;
    *)
      printf "\n%s" \
        "This script imports Terraform state from a Github Organization" \
        "Designate Github Organization by environment variable GITHUB_ORG" \
        "Eg. export GITHUB_ORG=\"<organization>\"" \
        "" \
        "Usage: $0 [members|teams|team-membership|all]" \
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
