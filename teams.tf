locals {
  teams = jsondecode(file("teams.json"))
}

resource "github_team" "teams" {
  for_each = { for t in local.teams : t.name => t }

  name                      = each.value.name
  description               = each.value.description == null ? "" : each.value.description
  privacy                   = each.value.privacy
  parent_team_id            = each.value.parent_team_id == null ? null : each.value.parent_team_id
  #create_default_maintainer = true
}
