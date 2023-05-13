locals {
  repositories = flatten([    for repo in jsondecode(file("repo-collaborators.json")) :    [      for team in repo["team:"] :
      [
        for user in repo["user"] :
        [
          for username in user["usernames"] :
          {
            repository = repo["repository"]
            team = length(team["team"]) > 0 ? team["team"][0] : null
            permission = length(team["permission"]) > 0 ? team["permission"][0] : null
            username = username
            user_permission = user["permission"][index(user["usernames"], username)]
          }
        ]
      ]
    ]
  ])
}

