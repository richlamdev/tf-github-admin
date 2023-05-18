locals {
  json_data = jsondecode(file("repo-collaborators.json"))

  user_data = flatten([
    for repo in local.json_data: [
      for user in repo.user: {
        repository      = repo.repository
        username        = user.username
        permission_user = user.permission
        team_id         = null
        permission_team = null
      }
    ]
  ])

  team_data = flatten([
    for repo in local.json_data: [
      for team in repo.team: {
        repository      = repo.repository
        username        = null
        permission_user = null
        team_id         = team.team_id
        permission_team = team.permission
      }
    ]
  ])

  prepared_data = concat(local.user_data, local.team_data)
}

resource "github_repository_collaborators" "repo_collaborators" {
  #for_each = { for item in local.prepared_data : "${item.repository}-${coalesce(item.username, "no_user")}-${coalesce(item.team_id, "no_team")}" => item }
  for_each = { for item in local.prepared_data : join("-", compact([item.repository, item.username != null ? item.username : "", item.team_id != null ? item.team_id : ""])) => item }


  repository = each.value.repository

  dynamic "user" {
    for_each = each.value.username != null ? [each.value] : []
    content {
      username  = user.value.username
      permission = user.value.permission_user
    }
  }

  dynamic "team" {
    for_each = each.value.team_id != null ? [each.value] : []
    content {
      team_id    = team.value.team_id
      permission = team.value.permission_team
    }
  }
}

