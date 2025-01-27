class Batter:
    def __init__(self, name, position, lineup_spot):
        self.name = name
        self.position= position
        self.lineup_spot = lineup_spot
        
    def to_dict(self):
        return {
            'Name': self.name,
            'Position': self.position,
            'LineupSpot': self.lineup_spot
        }
        
    def __str__(self):
        return f"Batter(Name={self.name}, Position={self.position}, LineupSpot={self.lineup_spot})"

    def __repr__(self):
        return f"Batter({self.name!r}, {self.position!r}, {self.lineup_spot!r})"