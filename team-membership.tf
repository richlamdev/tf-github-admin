#locals {
#  team_membership = jsondecode(file("team_memberships.json"))
#}
#
#resource "github_team_membership" "team_memberships" {
#  for_each = {
#    for team in local.team_membership :
#    team.id => {
#      team_id = team.id
#      member = {
#        for m in team.members :
#        m.username => {
#          username = m.username
#          role = m.role
#        }
#      }
#    }
#  }
#  team_id = each.value.team_id
#  username = each.value.members[*].username
#  role = each.value.members[*].role
#}

locals {
  team_membership = jsondecode(file("team_memberships.json"))
}

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

  team_id   = each.value.team_id
  username  = element(each.value.members[*].username, 0)
  role     = element(each.value.members[*].role,0)
}

