class Weather:
    def __init__(self, away_team, home_team, game_time, description, sentiment):
        self.away_team = away_team
        self.home_team = home_team
        self.game_time= game_time
        self.description = description
        self.sentiment = sentiment
    
    def to_dict(self):
        return {
            'AwayTeam': self.away_team,
            'HomeTeam': self.home_team,
            'GameTime': self.game_time,
            'Description': self.description,
            'Sentiment': self.sentiment
        }
        
    def __str__(self):
        return f"Weather(AwayTeam={self.away_team}, HomeTeam={self.home_team}, GameTime={self.game_time}, Description={self.description}, Sentiment={self.sentiment})"

    def __repr__(self):
        return f"Weather({self.away_team!r}, {self.home_team!r}, {self.game_time!r}, {self.description!r}, {self.sentiment!r})"
