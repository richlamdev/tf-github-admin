# variable "json_folder" {
#   description = "Folder containing the JSON files"
#   type        = string
#   default     = "./branch-protection"
# }

locals {
  branch_protection_json_files = fileset(path.module, "branch-protection/*.json")
}

resource "github_branch_protection_v3" "protection" {
  for_each = { for file in local.branch_protection_json_files : file => jsondecode(file(file)) }
  #for_each = { for file in local.branch_protection_json_files :
  #jsondecode(file(file)).repository => jsondecode(file(file)) }

  repository                  = each.value.repository
  branch                         = each.value.branch
  enforce_admins = contains(keys(each.value), "enforce_admins") ? each.value.enforce_admins : false
  require_signed_commits = contains(keys(each.value), "require_signed_commits") ? each.value.require_signed_commits : false
  require_conversation_resolution = contains(keys(each.value), "require_conversation_resolution") ? each.value.require_conversation_resolution : false
  # enforce_admins                 = each.value.enforce_admins
  # require_signed_commits         = each.value.require_signed_commits
  # require_conversation_resolution = each.value.require_conversation_resolution

  required_status_checks {
    strict  = contains(keys(each.value.required_status_checks), "strict") ? each.value.required_status_checks.strict : false
    #contexts = contains(keys(each.value.required_status_checks), "contexts") ? each.value.required_status_checks.contexts : []
    checks = contains(keys(each.value.required_status_checks), "checks") ? each.value.required_status_checks.checks : []
}

  required_pull_request_reviews {

    dismiss_stale_reviews = contains(keys(each.value.required_pull_request_reviews), "dismiss_stale_reviews") ? each.value.required_pull_request_reviews.dismiss_stale_reviews : false
    require_code_owner_reviews = contains(keys(each.value.required_pull_request_reviews), "require_code_owner_reviews") ? each.value.required_pull_request_reviews.require_code_owner_reviews : false
    required_approving_review_count = contains(keys(each.value.required_pull_request_reviews), "required_approving_review_count") ? each.value.required_pull_request_reviews.required_approving_review_count : 0
    bypass_pull_request_allowances {
      users = each.value.required_pull_request_reviews.bypass_pull_request_allowances.users
      teams = each.value.required_pull_request_reviews.bypass_pull_request_allowances.teams
    }
  }
  restrictions {
    users = each.value.restrictions.users
    teams = each.value.restrictions.teams
  }
}

