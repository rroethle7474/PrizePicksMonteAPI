class SingleTrialResult:
    def __init__(self, trial_num, is_win,bet_amount, win_amount):
        self.TrialNumber = trial_num
        self.IsWin = is_win
        self.BetAmount = round(bet_amount, 2)
        self.WinAmount = round(win_amount, 2)

    def to_dict(self):
        return {
            'TrialNumber': self.TrialNumber,
            'IsWin': self.IsWin,
            'BetAmount': self.BetAmount,
            'WinAmount': self.WinAmount
        }
        
    
    def __str__(self):
        return f"SingleTrialResult(TrialNumber={self.TrialNumber}, IsWin={self.IsWin}, BetAmount={self.BetAmount}, WinAmount={self.WinAmount})"

    def __repr__(self):
        return f"SingleTrialResult({self.TrialNumber!r}, {self.IsWin!r}, {self.BetAmount}, {self.WinAmount})"
