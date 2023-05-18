locals {
  json_data = jsondecode(file("repo-collaborators.json"))
}

resource "github_repository_collaborators" "repo_collaborators" {
  for_each = { for repo in local.json_data : repo.repository => repo }

  repository = each.value.repository

  dynamic "user" {
    for_each = each.value.user

    content {
      username  = user.value.username
      permission = user.value.permission
    }
  }

  dynamic "team" {
    for_each = each.value.team

    content {
      team_id    = team.value.team_id
      permission = team.value.permission
    }
  }
}

