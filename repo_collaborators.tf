# Define a `locals` block to flatten the JSON data
locals {
  flattened_data = flatten([
    for obj in jsondecode(file("repo-collaborators.json")) : {
      for team in obj.team : "team_${team.team[0]}_${obj.repository}" => {
        repository = obj.repository
        username = team.team[0]
        permission = team.permission[0]
      }
      for user in obj.user : [
        for i, username in enumerate(user.usernames) : {
          "user_${username}_${obj.repository}" => {
            repository = obj.repository
            username = username
            permission = user.permission[i]
          }
        }
      ]
    }
  ])
}

# Generate the Terraform resource file for GitHub repository collaborators
resource "github_repository_collaborators" "example" {
  for_each = local.flattened_data

  repository = each.value.repository
  username = each.value.username
  permission = each.value.permission
}

