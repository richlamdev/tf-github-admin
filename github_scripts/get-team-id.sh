##!/bin/bash
##

#ORG="$1"
#TEAM_NAME="$2"

#if [ "$#" -ne 2 ]; then
#    echo "Usage: $0 <org> <team-name>"
#    exit 1
#fi


#TEAM_ID=$(gh api "orgs/{$ORG}/teams")

#echo "Team ID: $TEAM_ID"

#if [ -z "$TEAM_ID" ]; then
#    echo "Team '$TEAM_NAME' not found"
#    exit 1
#fi

#echo "Team ID: $TEAM_ID"


#!/bin/bash
#

ORG="$1"
TEAM_NAME="$2"

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <org> <team-name>"
    exit 1
fi

TEAM_ID=$(gh api "orgs/${ORG}/teams" | python3 -c "import sys, json; print(next((item['id'] for item in json.load(sys.stdin) if item['name'] == '${TEAM_NAME}'), 'Team not found'))")

echo "Team ID: $TEAM_ID"

if [ "$TEAM_ID" == "Team not found" ]; then
    echo "Team '$TEAM_NAME' not found"
    exit 1
fi

echo "Team ID: $TEAM_ID"


