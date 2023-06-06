variable "json_dir" {
  description = "The directory where your JSON files are located"
  default     = "./repos/"
}

data "local_file" "json_files" {
  for_each = fileset(var.json_dir, "*.json")
  filename = "${var.json_dir}/${each.value}"
  #filename = each.value
}

resource "github_repository" "this" {
  for_each = {
    for name, file in data.local_file.json_files : name => jsondecode(file.content)
  }

  name                   = each.value.name
  description            = each.value.description
  homepage_url           = each.value.homepage_url
  private                = each.value.private
  has_issues             = each.value.has_issues
  has_projects           = each.value.has_projects
  has_wiki               = each.value.has_wiki
  allow_merge_commit     = each.value.allow_merge_commit
  allow_squash_merge     = each.value.allow_squash_merge
  allow_rebase_merge     = each.value.allow_rebase_merge
  delete_branch_on_merge = each.value.delete_branch_on_merge
  archived               = each.value.archived
  topics                 = each.value.topics

  // Assume Github provider supports these arguments
  vulnerability_alerts = each.value.vulnerability_alerts
  allow_update_branch  = each.value.allow_update_branch
}

