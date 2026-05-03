class Player_preview:
    def __init__(
        self,
        name,
        age,
        team,
        nationality,
        player_url,
        position,
        worth=0,
        player_img="",
        team_img="",
    ):
        self.name = name
        self.age = age
        self.team = team
        self.nationality = nationality
        self.player_img = player_img
        self.team_img = team_img
        self.player_url = player_url
        self.worth = worth
        self.position = position

    def __repr__(self):
        return f"""
    - Name: {self.name},
    - Team {self.team},
    - Nationality: {self.nationality},
    - Url: {self.player_url},
    - Worth: {self.worth},
    - Position: {self.position},
    """
