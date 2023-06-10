locals {
  data = jsondecode(file("repo-collaborators.json"))
}

resource "github_repository_collaborators" "collaborators" {
  for_each = local.data

  repository = each.key

  dynamic "user" {
    for_each = each.value.users
    content {
      username   = user.value.username
      permission = user.value.permission
    }
  }

  dynamic "team" {
    for_each = each.value.teams
    content {
      team_id    = team.value.team_id
      permission = team.value.permission
    }
  }
}

