import statsapi
from datetime import datetime, timedelta

class ScheduleService:
    
    def get_yesterday_game_ids():
        yesterday_date_string = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        games = statsapi.schedule(date=yesterday_date_string)
        unique_game_ids = set()
        for game in games:
        # Add the game_id to the set
            unique_game_ids.add(game['game_id'])
        unique_game_ids = list(unique_game_ids)
        box_score = statsapi.boxscore_data(unique_game_ids[0])
        # print(box_score)
        return box_score