class Pitcher:
    def __init__(self, name, handedness, wins, losses, era, strikeouts):
        self.name = name
        self.handedness = handedness
        self.wins= wins
        self.losses = losses
        self.era = era
        self.strikeouts = strikeouts
        
    def to_dict(self):
        return {
            'Name': self.name,
            'Hand': self.handedness,
            'Wins': self.wins,
            'Losses': self.losses,
            'ERA': self.era,
            'Strikeouts': self.strikeouts
        }
        
    def __str__(self):
        return f"Pitcher(Name={self.name}, Hand={self.handedness}, Wins={self.wins}, Losses={self.losses}, ERA={self.era}, Strikeouts={self.strikeouts})"

    def __repr__(self):
        return f"Pitcher({self.name!r}, {self.handedness!r}, {self.wins!r}, {self.losses!r}, {self.era!r}, {self.strikeouts!r})"