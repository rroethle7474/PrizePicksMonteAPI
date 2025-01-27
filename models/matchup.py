class Matchup:
    def __init__(self, away_team, home_team, game_time):
        self.away_team = away_team
        self.home_team = home_team
        self.game_time= game_time
    
    def to_dict(self):
        return {
            'AwayTeam': self.away_team.to_dict(),
            'HomeTeam': self.home_team.to_dict(),
            'GameTime': self.game_time
        }
        
    def __str__(self):
        return f"Matchup(AwayTeam={self.away_team}, HomeTeam={self.home_team}, GameTime={self.game_time})"

    def __repr__(self):
        return f"Matchup({self.away_team!r}, {self.home_team!r}, {self.game_time!r})"
