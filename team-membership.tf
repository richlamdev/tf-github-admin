locals {
  team_members = flatten([
    for team_member in jsondecode(file("team_memberships.json")) :
      [
	for member in team_member.members :
	  {
	    team_id     = team_member.id
	    team_name   = team_member.name
	    team_slug   = team_member.slug
	    username    = member.username
	    role        = member.role
	  }
      ]
  ])
}

resource "github_team_membership" "team_memberships" {
  for_each = { for member in local.team_members : "${member.team_id}-${member.username}" => member }

  team_id   = each.value.team_id
  username  = each.value.username
  role      = each.value.role
}
