locals {
  collaborators = jsondecode(file("repo-collaborators.json"))

  repository_collaborators = {
    for collab in local.collaborators :
     "${collab.repo}_${collab.user}" => {
      repository = collab.repo
      username   = collab.user
      permission = collab.permission
    }
  }
}

resource "github_repository_collaborator" "collaborator" {
  for_each = { for collab in local.repository_collaborators : "${collab.repository}-${collab.username}" => collab }

  repository = each.value.repository
  username   = each.value.username
  permission = each.value.permission
  permission_diff_suppression = true
}

