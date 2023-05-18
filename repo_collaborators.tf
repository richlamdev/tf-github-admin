locals {
  json_data = jsondecode(file("repo-collaborators.json"))

  flattened_user_data = flatten([
    for repo in local.json_data : [
      for user in repo.user : merge(
        { "repo_type" = "user" },
        { "repo_name" = repo.repository },
        user
      )]
  ])

  flattened_team_data = flatten([
    for repo in local.json_data : [
      for team in repo.team : merge(
        { "repo_type" = "team" },
        { "repo_name" = repo.repository },
        team
      )]
  ])
}



resource "github_repository_collaborators" "collaborators" {
  for_each = {
    #for item in local.flattened_data : "${item.repo_type}.${item.repo_name}.${item.username != null ? item.username : item.team_id}" => item
    for item in local.flattened_user_data : "${item.repo_name}-${item.username}" => item
  }

  repository = each.value.repo_name

  dynamic "user" {
    for_each = each.value.repo_type == "user" ? [each.value] : []

    content {
      username  = user.value.username
      permission = user.value.permission
    }
  }
}


resource "github_repository_collaborators" "team_collaborators" {
  for_each = {
    #for item in local.flattened_data : "${item.repo_type}.${item.repo_name}.${item.username != null ? item.username : item.team_id}" => item
    for item in local.flattened_team_data : "${item.repo_name}-${item.team_id}" => item
  }

  repository = each.value.repo_name

  dynamic "team" {
    for_each = each.value.repo_type == "team" ? [each.value] : []

    content {
      team_id    = team.value.team_id
      permission = team.value.permission
    }
  }
}

