data "local_file" "collaborators_json" {
  filename = "individual_collaborators.json"
}

locals {
  #collaborators_data = jsondecode(data.local_file.collaborators_json.content)
  collaborators_data = jsondecode(file("individual_collaborators.json"))
}

resource "github_repository_collaborators" "collaborator" {
  #for_each = { for repo, collaborators in local.collaborators_data : repo => collaborators }
  for_each = { for repo, collaborators in local.collaborators_data : "${repo}" => collaborators }

  repository = each.key
  dynamic "user" {
    for_each = each.value
    content {
      username   = user.value.username
      permission = user.value.permissions
    }
  }
  # Assuming no team block in this example, as it's not in the JSON input data
}

