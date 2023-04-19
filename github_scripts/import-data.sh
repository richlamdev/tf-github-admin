#/bin/bash

# usage:
#
# ./import-data.sh
#
# Requires gh cli and to be logged in with appropriate permissions to read
# (retrieve) all members from an organization
#


function get_team_membership {

  TEAM_FOLDER="../team-members/"

  echo "Checking if $TEAM_FOLDER exists: ${TEAM_FOLDER}"
  if [[ -d "${TEAM_FOLDER}" ]]; then
    echo "${TEAM_FOLDER} already exists"
  else
    echo "Creating ${TEAM_FOLDER}"
    mkdir "${TEAM_FOLDER}"
  fi

  printf "\n"
  printf "Get list of team memberhips from $ORG.\n"
  printf "\n"

  INPUT_FILE="../teams.csv"

  tail -n +2 $INPUT_FILE | while IFS=',' read -r null1 id null1 null2 null3 slug; do
    echo -n "" > "${TEAM_FOLDER}${id}-${slug}.csv"
    # Add the team ID to the output filename and include it in the file

    echo "teamid,username,role,teamslug" >> "${TEAM_FOLDER}${id}-${slug}.csv"

    team_member=$(gh api --paginate \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" /orgs/${ORG}/teams/$slug/members | \
    jq -r '.[] | "\(.login)"')
    readarray -t team_member_array <<< "$team_member"

    for member in "${team_member_array[@]}"; do
      team_member_role=$(gh api --paginate \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" /teams/$id/memberships/$member | \
      jq -r '.role')

      echo "$id,$member,$team_member_role,$slug" >> "${TEAM_FOLDER}${id}-${slug}.csv"
      # Append team members with their roles to the output file
    done

  done

  printf "\n"
  printf "List of team memberships written to ${TEAM_FOLDER}\n"
  printf "\n"
}


function get_teams {

  printf "\n"
  printf "Get list of teams from $ORG.\n"
  printf "\n"

  TEAMS_CSV="../teams.csv"
  printf "name,id,description,privacy,parent_team_id,slug\n" > $TEAMS_CSV
  printf "\n"

  gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /orgs/$ORG/teams | \
  jq -r '.[] | "\(.name),\(.id),\(.description // "null"),\(.privacy),\(.parent.id // "null"),\(.slug)"' >> $TEAMS_CSV

  printf "\n"
  printf "List of teams written to ${TEAMS_CSV}\n"
  printf "\n"
}


function get_members {

  printf "\n"
  printf "Get all members from $ORG.\n"
  printf "\n"

  users_array=($(gh api --paginate -H "Accept: application/vnd.github+json" \
                  -H "X-GitHub-Api-Version: 2022-11-28" \
                  /orgs/${ORG}/members | jq -r '.[].login'))

  printf "Get organization role for each user\n"
  printf "\n"

  USERS_CSV="../members.csv"
  printf "username,role\n" > $USERS_CSV

  for user in "${users_array[@]}"
  do
    gh api --paginate -H "Accept: application/vnd.github+json" \
           -H "X-GitHub-Api-Version: 2022-11-28" \
              /orgs/${ORG}/memberships/"${user}" | \
              jq -r '"\(.user.login),\(.role)"' >> $USERS_CSV
  done

  printf "List of members written to ${USERS_CSV}\n"
  printf "\n"
}


function main {

  echo
  echo "Checking if GITHUB_TOKEN is set via github (gh) cli."
  GH_STATUS=$(gh auth status)
  if [[ $? -ne 0 ]]; then
    echo
    echo "GITHUB_TOKEN is not set. Please set it and try again."
    echo "eg: export GITHUB_TOKEN=\"<github token>\""
    echo
    exit 1
  fi

  if [[ -z "${GITHUB_OWNER}" ]]; then
    echo
    echo "GITHUB_ORG is not set. Please set it and try again."
    echo "eg: export GITHUB_ORG=\"<organization name>\""
    echo
    exit 1
  fi


  case "$1" in
    members)
      get_members
      ;;
    teams)
      get_teams
      ;;
    team-membership)
      get_team_membership
      ;;
    all)
      get_members
      get_teams
      get_team_membership
      ;;
    *)
      printf "\n%s" \
        "This script scrapes data from a Github Organization" \
        "to import current Github state to Terraform state" \
        "" \
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
API_URL_PREFIX=${API_URL_PREFIX:-'https://api.github.com'}

main "$@"

exit 0
