locals {
  json_data = jsondecode(file("repo-collaborators.json"))
}

resource "github_repository_collaborators" "collaborators" {
  for_each   = { for repo in local.json_data : repo.repository => repo }
  repository = each.value.repository


  #username   = local.usernames
  #team_id    = local.team_id
  #permission = "pull"
}

