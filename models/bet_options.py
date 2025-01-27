# If WinningBet is in a separate file, you need to import it
from .winning_bet import WinningBet

class BetOptions:
    def __init__(self, bet_name, number_of_events, winning_bets=None, isPoweredUp=False):
        self.BetName = bet_name
        self.NumberOfEvents = number_of_events
        self.WinningBets = winning_bets if winning_bets is not None else []
        self.IsPoweredUp = isPoweredUp

    def add_winning_bet(self, winning_bet):
        self.WinningBets.append(winning_bet)