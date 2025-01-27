from db.fantasy_sports_db_entities.MLBWeatherReportMatchupEntity import MLBWeatherReportMatchupEntity
from db.fantasy_sports_db_entities.MLBWeatherReportEntity import MLBWeatherReportEntity
from datetime import datetime, date, time
from sqlalchemy import and_
from db.fantasy_sports_db import db
from db.DBResponse import DBResponse
import pytz

from services.logging_service import logger

class WeatherService():
    
    # this is an example of a method that uses multiple filtering
    # def get_weather_reports_by_date(self, date):
    #     print("DATE", date)
    #     return self.db.session.query(DailyMLBWeatherReport.DailyMLBWeatherReport).filter(and_(DailyMLBWeatherReport.DailyMLBWeatherReport.GameDate >= date,DailyMLBWeatherReport.DailyMLBWeatherReport.AwayTeam == "Angels")).all()

    def get_weather_reports_by_date(self, query_date):
        report_date = datetime.combine(query_date, time.min)
        get_report_for_today = db.session.query(MLBWeatherReportEntity).filter(MLBWeatherReportEntity.ReportDate == report_date).first()
        if get_report_for_today is not None:
            return db.session.query(MLBWeatherReportMatchupEntity).filter(MLBWeatherReportMatchupEntity.MLBWeatherReportXrefId == get_report_for_today.Id).all()
        else:
            return None
    
    def save_weather_report_today(self):
        try:
            report_date = datetime.combine(date.today(), time.min)
            new_report = MLBWeatherReportEntity(
                ReportDate=report_date,
                CreatedOn=datetime.now(),
                UpdatedOn=datetime.now()
            )
            db.session.add(new_report)
            db.session.commit()
            logger.info(f"New weather report created for {report_date}")
            return DBResponse(success=True, record_id=new_report.Id)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating new weather report: {str(e)}")
            return DBResponse(success=False, error=str(e))
    
    def save_weather_report(self, weather_data, report_id):
        try:
            new_report = MLBWeatherReportMatchupEntity(
                GameDate= self.convert_game_time(weather_data.game_time),
                MLBWeatherReportXrefId = report_id,
                AwayTeam=weather_data.away_team,
                HomeTeam=weather_data.home_team,
                GameDescription = weather_data.description,
                GameSentiment = weather_data.sentiment,
                CreatedOn = datetime.now(),
                UpdatedOn = datetime.now()
            )
            db.session.add(new_report)
            db.session.commit()
            return DBResponse(success=True, record_id=new_report.Id, record=new_report)
        except Exception as e:
            db.session.rollback()
            return DBResponse(success=False, error=str(e))


    def convert_game_time(self, input_string):
        # Extract the time part from the string
        time_str = input_string.split(', at ')[1].strip()  # gets 'at 2:20 PM  EST'
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