#locals {
#  teams = jsondecode(file("teams.json"))
#}
#
#resource "github_team" "teams" {
#  for_each = { for team in local.teams : team.name => team }
#
#  name            = each.value.name
#  description     = each.value.description
#  privacy         = each.value.privacy
#  #parent_team_id  = each.value.parent_team_id == "null" ? null : each.value.parent_team_id
#  parent_team_id = can(number(each.value.parent_team_id)) ? tonumber(each.value.parent_team_id) : null
#}


locals {
  teams = jsondecode(file("teams.json"))
}

resource "github_team" "teams" {
  for_each = { for team in local.teams : team.name => team }

  name                    = each.value.name
  description             = coalesce(each.value.description, "")
  privacy                 = each.value.privacy
  parent_team_id          = try(each.value.parent_team_id, null)
  create_default_maintainer = true
}

resource "github_team" "no_parent_teams" {
  for team in [for team in local.teams : team.parent_team_id == null || team.parent_team_id == "null"] {
    name                    = team.name
    description             = coalesce(team.description, "")
    privacy                 = team.privacy
    create_default_maintainer = true
  }
}

