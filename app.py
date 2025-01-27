from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS
import statistics
import requests
from datetime import datetime

from models.bet_options import BetOptions
from models.winning_bet import WinningBet
from models.results import TrialResult
from models.final_result import FinalResult
from models.single_trial_result import SingleTrialResult
from models.pitcher import Pitcher
from models.matchup import Matchup
from models.batter import Batter
from models.team import Team
from models.weather import Weather
from probability_service import ProbabilityService
from bs4 import BeautifulSoup
import unicodedata
from services.schedule_service import ScheduleService
from services.weather_service import WeatherService
from db.fantasy_sports_db import db
from db.DBResponse import DBResponse
from flask_caching import Cache
from services.logging_service import logger
from models.MLBWeatherReportMatchup import DailyMLBWeatherReport

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = r''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#TrustServerCertificate for driver 18
#Trusted_Connection=yes for driver 17
# app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://@LAPTOP-NCE9QH15\MSSQLSERVER01?driver=ODBC+Driver+17+for+SQL+Server'

db.init_app(app)  # Bind the db instance to the Flask app

app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 14400  # 4 hours in seconds

cache = Cache(app)

probability_service = ProbabilityService(prob_single_corrected=0.213, prob_extra_base_hit_corrected=0.124)
weather_service = WeatherService()
# event_probability = .55

options = [
    BetOptions("Two Power Play", 2, [WinningBet(2, 3)]),
    BetOptions("Three Power Play", 3, [WinningBet(3, 5)]),
    BetOptions("Three Flex Play", 3, [WinningBet(3, 2.25), WinningBet(2, 1.25)]),
    BetOptions("Four Power Play", 4, [WinningBet(4, 10)]),
    BetOptions("Four Flex Play", 4, [WinningBet(4, 5), WinningBet(3, 1.5)]),
    BetOptions("Four Power Power Play", 4, [WinningBet(4, 18)]),
    BetOptions("Five Flex Play", 5, [WinningBet(5, 10), WinningBet(4, 2), WinningBet(3, .4)]),
    BetOptions("Six Flex Play", 6, [WinningBet(6, 25), WinningBet(5, 2), WinningBet(4, .4)]),
    BetOptions("Six Flex Power Play", 6, [WinningBet(6, 38), WinningBet(5, 4), WinningBet(4,.4)])
]

def strip_accents(text):
    # Normalize the Unicode string to decompose the characters into base characters and their modifiers (like accents)
    text = unicodedata.normalize('NFD', text)
    # Filter out the characters that are not in the ASCII range, which removes the accents
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Replace specific accented characters if needed, for example:
    text = text.replace('í', 'i').replace('é', 'e')
    return text

def convert_to_number(text, data_type=float):
    # Remove non-numeric characters (including periods for floats)
    cleaned_text = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
    
    # Try converting the cleaned text to the specified data type (float or int)
    try:
        return data_type(cleaned_text)
    except ValueError:
        # Return 0 if conversion fails
        return 0

# Clean the 'era' field
def clean_era(era_text):
    # Assuming era_text is a list with a single string item
    era_value = era_text[0] if era_text else "-.--"
    return convert_to_number(era_value, float)

# Clean the 'strikeouts' field
def clean_strikeouts(strikeouts_text):
    # Assuming strikeouts_text is a list with a single string item
    strikeouts_value = strikeouts_text[0] if strikeouts_text else "0"
    return convert_to_number(strikeouts_value, int)

def transform_game_data(game):
    # Helper function to find the last non-null inning
    def find_last_inning(innings):
        # Find the keys of innings that have non-null values
        non_null_innings = [int(k) for k, v in innings.items() if v is not None]
        # Return the highest inning number if there are any, else default to 1
        return max(non_null_innings) if non_null_innings else 1
    
    print("GAME", game)
    brewer_score = {
        "gameTime": game["time"],  # Assuming this is already in US Central Date Time
        "status": game["status"]["long"],
        "awayTeam": {
            "team": game["teams"]["away"]["name"],
            "hits": game["scores"]["away"]["hits"] if game["scores"]["away"]["hits"] is not None else 0,
            "errors": game["scores"]["away"]["errors"] if game["scores"]["away"]["errors"] is not None else 0,
            "score": game["scores"]["away"]["total"] if game["scores"]["away"]["total"] is not None else 0,
            "inning": find_last_inning(game["scores"]["away"]["innings"])
        },
        "homeTeam": {
            "team": game["teams"]["home"]["name"],
            "hits": game["scores"]["home"]["hits"] if game["scores"]["home"]["hits"] is not None else 0,
            "errors": game["scores"]["home"]["errors"] if game["scores"]["home"]["errors"] is not None else 0,
            "score": game["scores"]["home"]["total"] if game["scores"]["home"]["total"] is not None else 0,
            "inning": find_last_inning(game["scores"]["home"]["innings"])
        }
    }

    return brewer_score


def monte_carlo_simulator(starting_income, number_of_bets, number_of_trials, bet_size, event_probability, power_probability = .9):
    final_results = []
    #np.random.seed(42)  # For reproducible results
    # looping over each trial
    for _ in range(number_of_trials):
        # looping over each option
        for option in options:
            total_income = starting_income
            num_events = option.NumberOfEvents
            total_bets = 0
            option_probability = event_probability if option.IsPoweredUp else event_probability * power_probability
            # loop through number of bets to place during trial
            for i in range(number_of_bets):
                wins = 0
                isWinner = False
                total_bets += 1
                for e in range(num_events):
                    win = np.random.rand() < option_probability
                    if win:
                        wins += 1
                for b in option.WinningBets:
                    if b.EventWinners == wins:
                        total_income += (bet_size * b.PayoutMultiplier) - bet_size
                        isWinner = True
                        break
                if not isWinner:
                    if(bet_size > total_income):
                        total_income = 0
                    else:
                        total_income -= bet_size
                if total_income <= 0:
                    total_income = 0 # Reset total income to 0 if it goes negative due to a win but lower payout multiplier.
                    break
            final_results.append(TrialResult(option.BetName ,total_bets, total_income))
    return final_results

def single_result_simulator(starting_income, number_of_bets, bet_size, event_probability, power_probability = .9):
    final_results = []
    #np.random.seed(42)  # For reproducible results
        # looping over each option
    for option in options:
        total_income = starting_income
        num_events = option.NumberOfEvents
        total_bets = 0
        option_probability = event_probability if option.IsPoweredUp else event_probability * power_probability
        trial_results = []
        # loop through number of bets to place during trial
        for i in range(number_of_bets):
            wins = 0
            isWinner = False
            total_bets += 1
            for e in range(num_events):
                win = np.random.rand() < option_probability
                if win:
                    wins += 1
            result = SingleTrialResult(i+1,isWinner,bet_size,0)
            for b in option.WinningBets:
                if b.EventWinners == wins:
                    total_income += (bet_size * b.PayoutMultiplier) - bet_size
                    isWinner = True
                    result.IsWin = True
                    result.WinAmount = (bet_size * b.PayoutMultiplier) - bet_size
                    break
            if not isWinner:
                if(bet_size > total_income):
                    total_income = 0
                else:
                    total_income -= bet_size
            if total_income <= 0:
                total_income = 0 # Reset total income to 0 if it goes negative due to a win but lower payout multiplier.
                break
            trial_results.append(result)
        final_results.append(TrialResult(option.BetName ,total_bets, total_income, trial_results))
    return final_results

@app.route('/simulatesingle', methods=['POST'])
def simulate_single():
    data = request.get_json()
    starting_income = data.get('starting_income', 1000)
    number_of_bets = data.get('number_of_bets', 10)
    bet_size = data.get('bet_size', 20)
    event_probability = data.get('event_probability', .50)
    power_probability = data.get('power_probability', .90)
    results = single_result_simulator(starting_income, number_of_bets, bet_size, event_probability, power_probability)
    return jsonify([result.to_dict() for result in results])



@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    starting_income = data.get('starting_income', 1000)
    number_of_bets = data.get('number_of_bets', 10)
    number_of_trials = data.get('number_of_trials', 2)
    bet_size = data.get('bet_size', 20)
    event_probability = data.get('event_probability', .50)
    power_probability = data.get('power_probability', .90)
    results = monte_carlo_simulator(starting_income, number_of_bets, number_of_trials, bet_size, event_probability, power_probability)
    # Group by BetName
    results_by_bet_name = {}
    for result in results:
        if result.BetName not in results_by_bet_name:
            results_by_bet_name[result.BetName] = []
        results_by_bet_name[result.BetName].append(result)

    # Analyze and store final results
    final_results = []
    for bet_name, results in results_by_bet_name.items():
        number_bets = [result.NumberBets for result in results]
        final_totals = [result.FinalTotal for result in results]
        
        # Calculate statistics, handling exceptions for mode
        try:
            mode_bets = statistics.mode(number_bets)
        except statistics.StatisticsError:
            mode_bets = None  # Or any default value you see fit
        
        try:
            mode_total = statistics.mode(final_totals)
        except statistics.StatisticsError:
            mode_total = None  # Or any default value
        
        final_result = FinalResult(
            bet_name,
            mean_bets=statistics.mean(number_bets),
            median_bets=statistics.median(number_bets),
            mode_bets=mode_bets,
            mean_total=statistics.mean(final_totals),
            median_total=statistics.median(final_totals),
            mode_total=mode_total,
            min_bet_number=min(number_bets),
            max_bet_number=max(number_bets),
            min_total=min(final_totals),
            max_total=max(final_totals),
            standard_deviation_bets= statistics.stdev(number_bets) if len(number_bets) > 1 else None,
            standard_deviation_total=statistics.stdev(final_totals) if len(final_totals) > 1 else None
        )
        final_results.append(final_result)
    return jsonify([result.to_dict() for result in final_results])

@app.route('/win_prob/', methods=['GET'])
@app.route('/win_prob/<int:min_at_bats>/<int:max_at_bats>', methods=['GET'])
def win_probability(min_at_bats=2, max_at_bats=5):
    single_prob = float(request.args.get('single_prob', '0.213')) # this is for the probability of getting a single
    double_prob = float(request.args.get('double_prob', '0.124')) # this is for the probability of getting an extra base hit
    
    results = probability_service.calculate_winning_probability("Christian Yelich",min_at_bats, max_at_bats, single_prob, double_prob)
    return jsonify({
        'prob_win_bet': results
    })
    
@app.route('/get_yesterday_games/', methods=['GET'])
def get_games():
    results = ScheduleService.get_yesterday_game_ids()
    return jsonify({
        'games': results
    })

# singles divided by total plate appearances    
# extra base hits divided by total plate appearances
# use previous year's stats if available .35
# use current year's stats - .5
# use last 10 games stats - .15
# pitcher factor
# handedness split factor
# away vs home factor


#https://api-sports.io/documentation/baseball/v1#section/Authentication
@app.route('/getmlbgames', methods=['GET'])
def get_mlb_games():
    # Assuming the API requires a date, format today's date as needed. If not, remove this part.
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Prepare the API request
    url = "https://api-baseball.p.rapidapi.com/games"
    # If the API requires a date, add it to the querystring: {"date": today}
    querystring = {"date": today, "league": "1", "season": "2024", "timezone": "America/Chicago", "team": "20"}
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "api-baseball.p.rapidapi.com"
    }
    
    # Make the API call
    response = requests.get(url, headers=headers, params=querystring)  # Add `, params=querystring` if needed
    
    # Check if the request was successful
    if response.status_code == 200:
        r_1 = response.json()
        brewer_game_score = transform_game_data(r_1["response"][0])
        # Return the JSON response directly
        return jsonify(brewer_game_score), 200
    else:
        # Handle possible errors (e.g., API not available, bad request, etc.)
        return jsonify({"error": "Failed to fetch MLB games"}), response.status_code
    
def get_pitcher(pitcher_div):
    name = pitcher_div.find('div', class_='starting-lineups__pitcher-name').text.strip()
    if name == "TBD":
        pitcher = Pitcher(name, "TBD", 0, 0, 0.00, 0)
        return pitcher
    
    handedness = pitcher_div.find('span', class_='starting-lineups__pitcher-pitch-hand').text.strip()
    stats_summary = pitcher_div.find('div', class_='starting-lineups__pitcher-stats-summary')
    
    wins = stats_summary.find('span', class_='starting-lineups__pitcher-wins').text.strip()
    losses = stats_summary.find('span', class_='starting-lineups__pitcher-losses').text.strip()
    era = stats_summary.find('span', class_='starting-lineups__pitcher-era').text.strip()
    strikeouts = stats_summary.find('span', class_='starting-lineups__pitcher-strikeouts').text.strip()
    
    return Pitcher(strip_accents(name), handedness, wins, losses, clean_era(era), clean_strikeouts(strikeouts))

def get_lineup(lineup_div):
    batters = []
    tbd_div = lineup_div.find('li', class_='starting-lineups__player--TBD')
    
    if tbd_div:
        return batters
    
    players = lineup_div.find_all('li', class_='starting-lineups__player')
    
    for index, player in enumerate(players, start=1):
        name = player.find('a', class_='starting-lineups__player--link').text.strip() if player.find('a', class_='starting-lineups__player--link') else ""
        position_text = player.find('span', class_='starting-lineups__player--position').text.strip() if player.find('span', class_='starting-lineups__player--position') else ""
        position = position_text.split()[-1] if position_text else ""
        
        batter = Batter(name, position, index)
        batters.append(batter)
        
    return batters

def fetch_mlb_starting_lineups():
    url = 'https://www.mlb.com/starting-lineups'
    response = requests.get(url)
    matchups = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        lineup_container = soup.find('section', class_='starting-lineups')
        matchups_div = lineup_container.find_all('div', class_='starting-lineups__matchup')
        index=0
        for matchup in matchups_div:
            index += 1
            away_team = matchup.find('span', class_='starting-lineups__team-name--away')
            home_team = matchup.find('span', class_='starting-lineups__team-name--home')
            game_time = matchup.find('div', class_='starting-lineups__game-date-time')

            # Using 'or' to assign a default value if None is found
            away_team_text = (away_team.text.strip() if away_team else "Unknown Away Team")
            home_team_text = (home_team.text.strip() if home_team else "Unknown Home Team")
            game_time_text = (game_time.text.strip() if game_time else "Unknown Game Time")
            
            print(f"Matchup: {away_team_text} vs. {home_team_text} at {game_time_text}")
            
            pitchers_divs = matchup.find_all('div', class_='starting-lineups__pitcher-summary')
            away_pitcher_div = pitchers_divs[0]
            home_pitcher_div = pitchers_divs[2]

            away_pitcher = get_pitcher(away_pitcher_div)
            home_pitcher = get_pitcher(home_pitcher_div)
            
            away_lineup_div = matchup.find('ol', class_='starting-lineups__team starting-lineups__team--away')
            home_lineup_div = matchup.find('ol', class_='starting-lineups__team starting-lineups__team--home')

            away_lineup = get_lineup(away_lineup_div)
            home_lineup = get_lineup(home_lineup_div)

            away_team = Team(away_team_text, away_pitcher, away_lineup)
            home_team = Team(home_team_text, home_pitcher, home_lineup)

            game_matchup = Matchup(away_team, home_team, game_time_text)
            matchups.append(game_matchup)
    else:
        print(f"Failed to fetch the data. Status code: {response.status_code}")
        
    return matchups

@app.route('/getmlbstartinglineups', methods=['GET'])
def get_mlb_starting_lineups():
    # Assuming the API requires a date, format today's date as needed. If not, remove this part.
    response = fetch_mlb_starting_lineups()
    response_dicts = [matchup.to_dict() for matchup in response]
    
    return jsonify(response_dicts)
    # Check if the request was successful
    # if response.status_code == 200:
    #     r_1 = response.json()
    #     # Return the JSON response directly
    #     return jsonify(response), 200
    # else:
    #     # Handle possible errors (e.g., API not available, bad request, etc.)
    #     return jsonify({"error": "Failed to fetch MLB games"}), response.status_code

def fetch_mlb_weather_report_daily():
    url = 'https://www.rotowire.com/baseball/weather.php'
    response = requests.get(url)
    weather_matchups = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        weather_container = soup.find('div', class_='weather-boxes')
        weather_details = weather_container.find_all('div', class_='weather-box')
        for weather in weather_details:
            away_team = weather.find('a', class_='weather-box__team is-visit')
            home_team = weather.find('a', class_='weather-box__team is-home')
            game_time = weather.find('div', class_='weather-box__date')
            description = weather.find('div', class_='weather-box__weather')
            description_box = description.find('div', class_='text-80')
            sentiment = weather.find('div', class_='weather-box__notes')

            # Using 'or' to assign a default value if None is found
            away_team_text = (away_team.text.strip() if away_team else "Unknown Away Team")
            home_team_text = (home_team.text.strip() if home_team else "Unknown Home Team")
            game_time_text = (game_time.text.strip() if game_time else "Unknown Game Time")
            sentiment = (sentiment.text.strip() if sentiment else "Unknown Sentiment")
            description_text = (description_box.text.strip() if description_box else "Unknown Description")
            
            # print(f"Weather: {away_team_text} vs. {home_team_text} at {game_time_text}")
            # print(f"Description: {description_text}")
            # print(f"Sentiment: {sentiment}")
            weather_matchup = Weather(away_team_text, home_team_text, game_time_text, description_text, sentiment)
            weather_matchups.append(weather_matchup)
    else:
        print(f"Failed to fetch the weather data. Status code: {response.status_code}")
    #print(weather_matchups)
    return weather_matchups


# 
def map_entity_to_dto(entity):
        return DailyMLBWeatherReport(
            game_date=entity.GameDate,
            away_team=entity.AwayTeam,
            home_team=entity.HomeTeam,
            game_description=entity.GameDescription,
            game_sentiment=entity.GameSentiment,
            created_on=entity.CreatedOn,
            last_updated_on=entity.UpdatedOn
        )

@app.route('/langchain', methods=['GET'])
def try_rag():
    # Assuming the API requires a date, format today's date as needed. If not, remove this part.
    todayDate = datetime.now()
    print ("TODAY DATE", todayDate)
    logger.info(f"Fetching weather reports for {todayDate}")
    t = weather_service.get_weather_reports_by_date(todayDate)
    weather_matchups_dicts = [map_entity_to_dto(weather_matchup).to_dict() for weather_matchup in t]
    # determine when/how often to fetch weather data and if it will change
    print("T", t)
    
    return jsonify({"weather_matchups": weather_matchups_dicts})


@app.route('/getmlbdailyweather', methods=['GET'])
def get_mlb_daily_weather():
    # Assuming the API requires a date, format today's date as needed. If not, remove this part.
    todayDate = datetime.now()
    print ("TODAY DATE", todayDate)
    logger.info(f"Fetching weather reports for {todayDate}")
    t = weather_service.get_weather_reports_by_date(todayDate)
    weather_matchups_dicts = [map_entity_to_dto(weather_matchup).to_dict() for weather_matchup in t]
    # determine when/how often to fetch weather data and if it will change
    print("T", t)
    
    return jsonify({"weather_matchups": weather_matchups_dicts})
    # existing_weather_matchups = cache.get('weather_matchups')
    # if existing_weather_matchups:
    #     return jsonify({"weather_matchups": existing_weather_matchups})
    # weather_matchups = fetch_mlb_weather_report_daily()
    # weather_matchups_dicts = [weather_matchup.to_dict() for weather_matchup in weather_matchups]
    
    # weather_report_response = weather_service.save_weather_report_today()
    
    # cache.set('weather_matchups', weather_matchups_dicts, timeout=400)

    # if weather_report_response.success and weather_report_response.record_id is not None:
    #     report = weather_report_response.record_id
    #     all_records_saved = True
    #     for weather in weather_matchups:
    #         weather_report_matchup_response = weather_service.save_weather_report(weather, weather_report_response.record_id)
    #         if weather_report_matchup_response.success is False:
    #             all_records_saved = False
    #             break
    #     if all_records_saved:
    #         weather_matchups_dicts = [weather_matchup.to_dict() for weather_matchup in weather_matchups]
    #         return jsonify({"weather_matchups": weather_matchups_dicts})
    #     else:
    #         return jsonify({"error": "Failed to save weather reports matchups"})
    # else:
    #     return jsonify({"error": "Failed to save weather report"})


if __name__ == '__main__':
    app.run(debug=True)