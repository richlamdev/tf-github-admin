locals {
  team_membership = jsondecode(file("team_memberships.json"))
}

#resource "github_team_membership" "team_memberships" {
#  for_each = {
#    for team in local.team_membership :
#    team.id => {
#      team_id = team.id
#      members = [
#        for m in team.members :
#        {
#          username = m.username
#          role = m.role
#        }
#      ]
#    }
#  }
#
#  team_id   = each.value.team_id
#  username  = element(each.value.members[*].username, 0)
#  role     = element(each.value.members[*].role,0)
#}

resource "github_team_membership" "team_memberships" {
  for_each = {
    for team in local.team_membership :
    team.id => {
      team_id = team.id
      members = [
        for m in team.members :
        {
          username = m.username
          role = m.role
        }
      ]
    }
  }

  for member in each.value.members :
  username  = member.username
  role      = member.role
  team_id   = each.value.team_id
}





output "team_memberships" {
  value = github_team_membership.team_memberships.*
}
