from datetime import datetime
import pytz

class DailyMLBWeatherReport:
    def __init__(self, game_date, away_team, home_team, game_description, game_sentiment, created_on, last_updated_on):
        #self.GameDate = DailyMLBWeatherReport.convert_game_time(game_date)
        if isinstance(game_date, datetime):
            self.GameDate = game_date
        else:
            self.GameDate = DailyMLBWeatherReport.convert_game_time(game_date)
        
        self.AwayTeam = away_team
        self.HomeTeam = home_team
        self.GameDescription = game_description
        self.GameSentiment = game_sentiment
        self.CreatedOn = created_on #datetime.strptime(created_on, '%m/%d/%y')
        self.LastUpdatedOn = last_updated_on #datetime.strptime(last_updated_on, '%m/%d/%y')
    
    def convert_game_time(input_string):
        # Extract the time part from the string
        time_str = input_string.split('at')[1].strip()  # gets 'at 2:20 PM  EST'
        time_str = ' '.join(time_str.split()[:2])  # keeps '2:20 PM'

        # Parse the time string into a datetime object assuming it's in Eastern Time
        eastern = pytz.timezone('US/Eastern')
        time_format = '%I:%M %p'
        naive_time = datetime.strptime(time_str, time_format)
        aware_time = eastern.localize(naive_time)

        # Convert to Central Time
        central = pytz.timezone('US/Central')
        central_time = aware_time.astimezone(central)

        # Combine with today's date
        today = datetime.now().date()
        result_datetime = datetime.combine(today, central_time.timetz(), tzinfo=central)

        return result_datetime
        
    def to_dict(self):
        return {
            'AwayTeam': self.AwayTeam,
            'HomeTeam': self.HomeTeam,
            'GameTime': self.GameDate,
            'Description': self.GameDescription,
            'Sentiment': self.GameSentiment
        }
        
    def __str__(self):
        return f"DailyMLBWeatherReport(AwayTeam={self.AwayTeam}, HomeTeam={self.HomeTeam}, GameTime={self.GameDate}, Description={self.GameDescription}, Sentiment={self.GameSentiment}, CreatedOn={self.CreatedOn}, LastUpdatedOn={self.LastUpdatedOn})"