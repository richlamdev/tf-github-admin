locals {
  members = jsondecode(file("members.json"))
}

resource "github_membership" "member" {
  for_each = { for member in local.members : member.username => member }

  username = each.value.username
  role     = each.value.role
}

#output "members" {
  #value = github_membership.member
#}
