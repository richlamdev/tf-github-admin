#!/bin/bash

function members_import {

  INPUT_FILE="members.csv"
  OUTPUT_FILE="import_members.tf"

  echo "Checking if $OUTPUT_FILE exists."
  if [[ -f $OUTPUT_FILE ]]; then
    echo "[ Deleting $OUTPUT_FILE ]"
    echo
    rm $OUTPUT_FILE
  fi

  tail -n +2 $INPUT_FILE | while IFS=',' read -r username role; do

    config="resource \"github_membership\" \"$username\" {\n"
    config+="  username = \"$username\"\n"
    config+="  role = \"$role\"\n"
    config+="}\n"
    echo -e "$config" >> $OUTPUT_FILE

    terraform import github_membership.$username $ORG:$username

  done
}

function teams_import {

  INPUT_FILE="teams.csv"
  OUTPUT_FILE="import_teams.tf"

  echo "Checking if $OUTPUT_FILE exists."
  if [[ -f $OUTPUT_FILE ]]; then
    echo "[ Deleting $OUTPUT_FILE ]"
    echo
    rm $OUTPUT_FILE
  fi

  # Read the CSV file and loop over each line
  tail -n +2 $INPUT_FILE | while IFS=',' read -r name id description privacy parent_team_id slug; do

    # Set the slug variable using the name with spaces removed
    #slug=$(echo "$name" | tr -d '[:space:]')

    # Define the variable name using the slug
    var_name="${slug}_name"

    # Define the Terraform configuration for the team resource
    config="resource \"github_team\" \"$slug\" {\n"
    config+="  name = var.$var_name\n"
    config+="  description = \"$description\"\n"
    config+="  privacy = \"$privacy\"\n"

    # If parent_team_id is specified, add it to the configuration
    if [ -n "$parent_team_id" ]; then
      parent_slug=$(echo "$parent_team_id" | tr -d '[:space:]')
      config+="  parent_team_id = $parent_slug\n"
    fi

    # Close the configuration block
    config+="}\n"

    # Define the variable for the team name
    var_config="variable \"$var_name\" {\n"
    var_config+="  default = \"$name\"\n"
    var_config+="}\n"

    # Append the configuration to $OUTPUT_FILE
    echo -e "$config" >> $OUTPUT_FILE
    echo -e "$var_config" >> $OUTPUT_FILE

    terraform import github_team.$slug $id

  done
}


function team_membership_import {

  TEAM_MEMBERSHIP_OUTPUT_FILE="import_team_membership.tf"

  echo "Checking if $TEAM_MEMBERSHIP_OUTPUT_FILE exists."
  if [[ -f $TEAM_MEMBERSHIP_OUTPUT_FILE ]]; then
    echo "[ Deleting $TEAM_MEMBERSHIP_OUTPUT_FILE ]"
    echo
    rm $TEAM_MEMBERSHIP_OUTPUT_FILE
    #read -p "press enter to continue"
  fi

  for file in team-members/*; do

    tail -n +2 $file | while IFS=',' read -r teamid username role slugteam; do

    #echo $teamid, $username
    slug_teamname=$(echo "$slugteam" | tr '-' '_')
    slug_username=$(echo "$username" | tr '-' '_')

    config="resource \"github_team_membership\" \""${slug_teamname}"_"${slug_username}"\" {\n"
    config+="  team_id = $teamid\n"
    config+="  username = \"$username\"\n"
    config+="  role = \"$role\"\n"
    config+="}\n"
    echo -e "$config" >> $TEAM_MEMBERSHIP_OUTPUT_FILE

    terraform import github_team_membership.${slug_teamname}"_"${slug_username}  $teamid:$username

    done
  done
}


function main {

  case "$1" in
    members)
      members_import
      ;;
    teams)
      teams_import
      ;;
    team-membership)
      team_membership_import
      ;;
    all)
      members_import
      teams_import
      team_membership_import
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
