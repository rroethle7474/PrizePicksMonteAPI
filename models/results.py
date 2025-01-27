class TrialResult:
    def __init__(self, betName, number_bets, final_total, trial_results=None):
        self.BetName = betName
        self.NumberBets = number_bets
        self.FinalTotal = round(final_total, 2)
        self.TrialResults = trial_results

    def to_dict(self):
        return {
            'BetName': self.BetName,
            'TotalBets': self.NumberBets,
            'FinalTotal': self.FinalTotal,
            'TrialResults': [result.to_dict() for result in self.TrialResults]
        }
        
    
    def __str__(self):
        return f"TrialResult(BetName={self.BetName}, NumberBets={self.NumberBets}, FinalTotal={self.FinalTotal}, TrialResults={self.TrialResults})"

    def __repr__(self):
        return f"TrialResult({self.BetName!r}, {self.NumberBets!r}, {self.FinalTotal!r}, {self.TrialResults})"
