locals {
  json_files = fileset(path.module, "repos/*.json")

  repositories = {
    for file in local.json_files :
    jsondecode(file(file)).name => jsondecode(file(file))
  }
}

resource "github_repository" "repo" {
  for_each = local.repositories

  name                    = each.value.name
  description             = each.value.description
  homepage_url            = each.value.homepage_url
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
  squash_merge_commit_title = each.value.squash_merge_commit_title
  squash_merge_commit_message = each.value.squash_merge_commit_message
  merge_commit_title       = each.value.merge_commit_title
  merge_commit_message     = each.value.merge_commit_message
  delete_branch_on_merge  = each.value.delete_branch_on_merge
  has_downloads           = each.value.has_downloads
  archived                = each.value.archived
  topics                  = each.value.topics
  vulnerability_alerts    = each.value.vulnerability_alerts
  allow_update_branch     = each.value.allow_update_branch
  lifecycle {
    ignore_changes = [pages,template]
  }
}

