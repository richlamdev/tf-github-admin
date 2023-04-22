#!/bin/bash


function import_members() {

  INPUT_FILE="members.json"
  OUTPUT_FILE="import_members.tf"
  EOF_MARKER="END_OF_FILE_MARKER"

  echo "Checking if $OUTPUT_FILE exists."
  if [[ -f $OUTPUT_FILE ]]; then
    echo "[ Deleting $OUTPUT_FILE ]"
    echo
    rm $OUTPUT_FILE
  fi

  # Loop through each member in the JSON file
  jq -c '.[]' $INPUT_FILE | while read -r json; do
    username=$(echo $json | jq -r '.username')
    role=$(echo $json | jq -r '.role')

    config=$(cat <<-EOF
resource "github_membership" "$username" {
  username = "$username"
  role     = "$role"
}\n
EOF
)

    # Write the Terraform resource to the output file
    echo -e "$config" >> $OUTPUT_FILE

    # Import the state for the member
    terraform import github_membership.$username $ORG:$username
  done
}


function import_teams {

  INPUT_FILE="teams.json"
  OUTPUT_FILE="import_teams.tf"

  echo "Checking if $OUTPUT_FILE exists."
  if [[ -f $OUTPUT_FILE ]]; then
    echo "[ Deleting $OUTPUT_FILE ]"
    echo
    rm $OUTPUT_FILE
  fi

  # Read the JSON file and loop over each object
  jq -c '.[]' $INPUT_FILE | while read -r team; do
    name=$(echo "$team" | jq -r '.name')
    id=$(echo "$team" | jq -r '.id')
    description=$(echo "$team" | jq -r '.description')
    privacy=$(echo "$team" | jq -r '.privacy')
    parent_team_id=$(echo "$team" | jq -r '.parent_team_id')
    slug=$(echo "$team" | jq -r '.slug')

    # Define the variable name using the slug
    var_name="${slug}_name"

    # Define the Terraform configuration for the team resource
    config=$(cat <<-EOF
resource "github_team" "$slug" {
  name = var.$var_name
  description = $(if [ "$description" != "null" ]; then echo "\"$description\""; else echo "null"; fi)
  create_default_maintainer = true
  privacy = "$privacy"\n
EOF
)

    # If parent_team_id is specified, add it to the configuration
    if [ "$parent_team_id" != "null" ]; then
      parent_slug=$(echo "$parent_team_id" | tr -d '[:space:]')
      config+="  parent_team_id = $parent_slug\n"
    else
      config+="  parent_team_id = null\n"
    fi

    # Close the configuration block
    config+="}"

    # Define the variable for the team name
    var_config=$(cat <<-EOF
variable "$var_name" {
  default = "$name"
}\n
EOF
)

    # Append the configuration to $OUTPUT_FILE
    echo -e "$config" >> $OUTPUT_FILE
    echo -e "$var_config" >> $OUTPUT_FILE

    terraform import github_team.$slug $id

  done
}


function import_team_membership {

  TEAM_MEMBERSHIP_OUTPUT_FILE="import_team_membership.tf"
  JSON_FILE="team_memberships.json"

  echo "Checking if $TEAM_MEMBERSHIP_OUTPUT_FILE exists."
  if [[ -f $TEAM_MEMBERSHIP_OUTPUT_FILE ]]; then
    echo "[ Deleting $TEAM_MEMBERSHIP_OUTPUT_FILE ]"
    echo
    rm $TEAM_MEMBERSHIP_OUTPUT_FILE
  fi

  jq -c '.[]' $JSON_FILE | while read line; do
    team_id=$(echo $line | jq -r '.id')
    team_slug=$(echo $line | jq -r '.slug')
    members=$(echo $line | jq -c '.members[]')

    while read member; do
      username=$(echo $member | jq -r '.username')
      role=$(echo $member | jq -r '.role')

      slug_teamname=$(echo "$team_slug" | tr '-' '_')
      slug_username=$(echo "$username" | tr '-' '_')

      cat << EOF >> $TEAM_MEMBERSHIP_OUTPUT_FILE
resource "github_team_membership" "${slug_teamname}_${slug_username}" {
  team_id  = $team_id
  username = "$username"
  role     = "$role"
}

EOF

      terraform import github_team_membership.${slug_teamname}_${slug_username} $team_id:$username

    done <<< "$members"
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
