class FinalResult:
    def __init__(self, betName, mean_bets, median_bets, mode_bets, 
                 mean_total, median_total, mode_total, min_bet_number, 
                 max_bet_number, min_total, max_total, standard_deviation_bets=None, standard_deviation_total=None):
        self.BetName = betName
        self.MeanBets = mean_bets
        self.MedianBets = median_bets
        self.ModeBets = mode_bets
        self.MinBetNumber = min_bet_number
        self.MaxBetNumber = max_bet_number
        self.MeanTotal = mean_total
        self.MedianTotal = median_total
        self.ModeTotal = mode_total
        self.MinTotal = min_total
        self.MaxTotal = max_total
        self.StandardDeviationBets = standard_deviation_bets
        self.StandardDeviationTotal = standard_deviation_total
        
        
    def to_dict(self):
        return {
            'BetName': self.BetName,
            'MeanBets': self.MeanBets,
            'MedianBets': self.MedianBets,
            'ModeBets': self.ModeBets,
            'MinBetNumber': self.MinBetNumber,
            'MaxBetNumber': self.MaxBetNumber,
            'MeanTotal': self.MeanTotal,
            'MedianTotal': self.MedianTotal,
            'ModeTotal': self.ModeTotal,
            'MinTotal': self.MinTotal,
            'MaxTotal': self.MaxTotal,
            'StandardDeviationBets': self.StandardDeviationBets,
            'StandardDeviationTotal': self.StandardDeviationTotal
        }
        
    def __str__(self):
        return (f"FinalResult(BetName={self.BetName}, MeanBets={self.MeanBets}, "
                f"MedianBets={self.MedianBets}, ModeBets={self.ModeBets}, "
                f"MeanTotal={self.MeanTotal}, MedianTotal={self.MedianTotal}, ModeTotal={self.ModeTotal})")

    def __repr__(self):
        return (f"FinalResult({self.BetName!r}, {self.MeanBets!r}, {self.MedianBets!r}, "
                f"{self.ModeBets!r}, {self.MeanTotal!r}, {self.MedianTotal!r}, {self.ModeTotal!r})")