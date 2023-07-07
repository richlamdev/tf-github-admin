#!/bin/bash
set -x

IFS=$'\n'   # change the field separator to newline only
resources=$(terraform state list | grep -P 'github_team\.teams\[".* .*"\]')
echo "Resources to remove: $resources"

for resource in $resources; do
  echo "Removing resource: $resource"
  terraform state rm "$resource"
done

echo "Script finished"

