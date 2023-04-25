locals {
  team_membership = jsondecode(file("team_memberships.json"))
}

resource "github_team_membership" "team_memberships" {
  for_each = {
    for team in local.team_membership :
    team.id => {
      team_id = team.id
      member = {
        for m in team.members :
        m.username => {
          username = m.username
          role = m.role
        }
      }
    }
  }
}
