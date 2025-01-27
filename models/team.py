class Team:
    def __init__(self, name, pitcher, lineup):
        self.name = name
        self.pitcher = pitcher
        self.lineup = lineup # array of batters
        
    def to_dict(self):
        print(self.pitcher.to_dict())
        print(self.name)
        return {
            'Name': self.name,
            'Pitcher': self.pitcher.to_dict(),
            'Lineup': [batter.to_dict() for batter in self.lineup]
        }
    
    def __str__(self):
        return f"Team(Name={self.name}, Pitcher={self.pitcher}, Lineup={self.lineup})"

    def __repr__(self):
        return f'Team({self.name!r}, {self.pitcher!r}, {self.lineup!r})'