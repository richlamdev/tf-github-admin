locals {
  json_files = fileset(path.module, "repos/*.json")

  repositories = {
    for file in local.json_files :
    jsondecode(file(file)).name => jsondecode(file(file))
    #file => jsondecode(file(file))
  }
}

resource "github_repository" "repo" {
  for_each = local.repositories

  name                    = each.value.name
  description             = each.value.description
  homepage_url            = each.value.homepage_url
  #private                 = each.value.private
  visibility              = each.value.visibility
  has_issues              = each.value.has_issues
  has_discussions         = each.value.has_discussions
  has_projects            = each.value.has_projects
  has_wiki                = each.value.has_wiki
  is_template             = each.value.is_template
  allow_merge_commit      = each.value.allow_merge_commit
  allow_squash_merge      = each.value.allow_squash_merge
  allow_rebase_merge      = each.value.allow_rebase_merge
  allow_auto_merge        = each.value.allow_auto_merge
  delete_branch_on_merge  = each.value.delete_branch_on_merge
  has_downloads           = each.value.has_downloads
  #default_branch          = each.value.default_branch
  archived                = each.value.archived
}

