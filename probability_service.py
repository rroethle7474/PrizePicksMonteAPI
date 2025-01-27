from scipy.stats import binom
import statsapi

class ProbabilityService:
    def __init__(self, prob_single_corrected, prob_extra_base_hit_corrected):
        self.prob_single_corrected = prob_single_corrected
        self.prob_extra_base_hit_corrected = prob_extra_base_hit_corrected

    # assumes playerName has been formatted properly and has whitespace stripped
    def calculate_winning_probability(self, playerName = None, min_at_bats=2, max_at_bats=5, prob_single = None, prob_extra_base_hit = None):
        # Validate min and max at bats
        print("SINGLE", prob_single)
        print("DOUBLE", prob_extra_base_hit)
        if playerName is None: ## need a player to retrieve stats
            return None
        
        self.prob_single_corrected = prob_single if prob_single is not None else self.prob_single_corrected
        self.prob_extra_base_hit_corrected = prob_extra_base_hit if prob_extra_base_hit is not None else self.prob_extra_base_hit_corrected
        
        player_stats = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'R'})['people'] if x['fullName']==playerName), 'hitting', 'yearByYear') # career, season, or yearByYear

        player_split_stats_id = next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'R'})['people'] if x['fullName']==playerName)
        
        # situation codes https://statsapi.mlb.com/api/v1/situationCodes
        params = {'personIds':player_split_stats_id, 'hydrate':'stats(group=[hitting],type=[statSplits],sitCodes=[vr,vl])'}
        paramsl10 = {'personIds':player_split_stats_id, 'hydrate':'stats(group=[hitting],type=[lastXgames],limit=1)'}
        people = statsapi.get('people',paramsl10)
        print("HMMMM", people)
        num_player_stats = len(player_stats['stats'])
        
        if num_player_stats < 1:
            return None
        
        current_year_player_stats = player_stats['stats'][-1]
        
        previous_year_player_stats = player_stats['stats'][-2] if num_player_stats > 1 else None
        
        if min_at_bats < 2 or max_at_bats < min_at_bats or max_at_bats > 10:
            min_at_bats = 2
            max_at_bats = 5

        # Array to hold the win probabilities for each number of at bats
        win_probabilities = {}

        for at_bats in range(min_at_bats, max_at_bats + 1):
            # Probability of getting at least two singles
            prob_two_singles = sum(binom.pmf(k, at_bats, self.prob_single_corrected) for k in range(2, at_bats + 1))
            
            # Probability of getting at least one extra-base hit
            prob_one_extra_base_hit = sum(binom.pmf(k, at_bats, self.prob_extra_base_hit_corrected) for k in range(1, at_bats + 1))
            
            # Probability of getting exactly one single and at least one extra-base hit
            prob_exactly_one_single = binom.pmf(1, at_bats, self.prob_single_corrected)
            prob_one_single_one_extra = prob_exactly_one_single * sum(binom.pmf(k, at_bats - 1, self.prob_extra_base_hit_corrected) for k in range(1, at_bats))
            
            # Summing probabilities for all winning scenarios
            prob_win_bet = prob_two_singles + prob_one_extra_base_hit + prob_one_single_one_extra
            win_probabilities[at_bats] = prob_win_bet

        return win_probabilities
    
    def calculate_hitter_walk_probablity(self, at_bats, num_walks):
        # Probability of getting at least one walk
        prob_one_walk = sum(binom.pmf(k, at_bats, self.prob_single_corrected) for k in range(1, at_bats + 1))
        
        return prob_one_walk
    
    def calculate_hitter_run_probability(self,at_bats, runs):
        prob_one_run = sum(binom.pmf(k, at_bats, self.prob_single_corrected) for k in range(1, at_bats + 1))
        
        return prob_one_run
        
    def calculate_hitter_rbi_probability(self, at_bats, rbis):
        prob_one_rbi = sum(binom.pmf(k, at_bats, self.prob_single_corrected) for k in range(1, at_bats + 1))
        
        return prob_one_rbi
        
        
    #https://github.com/toddrob99/MLB-StatsAPI/wiki/Examples documentation
    def weighted_average_probabilities(weights, probabilities):
        weighted_prob = sum(w * p for w, p in zip(weights, probabilities))
        total_weight = sum(weights)
        return weighted_prob / total_weight if total_weight > 0 else 0   
    
    def adjust_probability(base_prob, pitcher_adjustment, handedness_adjustment, home_away_adjustment):
        adjusted_prob = base_prob * pitcher_adjustment * handedness_adjustment * home_away_adjustment
        return adjusted_prob 
    
    # def predict_outcome(self, player_id, at_bats):
    #     # Retrieve stats
    #     last_year_stats = get_stats(player_id, 'last_year')
    #     current_year_stats = get_stats(player_id, 'current_year')
    #     last_10_games_stats = get_stats(player_id, 'last_10_games')

    #     # Calculate probabilities
    #     last_year_prob = self.calculate_winning_probability(last_year_stats['single'], last_year_stats['double'], at_bats)
    #     current_year_prob = self.calculate_winning_probability(current_year_stats['single'], current_year_stats['double'], at_bats)
    #     last_10_games_prob = self.calculate_winning_probability(last_10_games_stats['single'], last_10_games_stats['double'], at_bats)

    #     # Weighted average
    #     weights = [0.35, 0.5, 0.15]
    #     base_prob = self.weighted_average_probabilities(weights, [last_year_prob, current_year_prob, last_10_games_prob])

    #     # Adjustments
    #     pitcher_adjustment = get_pitcher_factor(player_id)
    #     handedness_adjustment = get_handedness_factor(player_id)
    #     home_away_adjustment = get_home_away_factor(player_id)

    #     # Final probability
    #     final_prob = adjust_probability(base_prob, pitcher_adjustment, handedness_adjustment, home_away_adjustment)

    #     return final_prob

