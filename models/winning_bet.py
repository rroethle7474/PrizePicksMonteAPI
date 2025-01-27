class WinningBet:
    def __init__(self, event_winners, payout_multiplier):
        self.EventWinners = event_winners
        self.PayoutMultiplier = round(payout_multiplier, 2)
