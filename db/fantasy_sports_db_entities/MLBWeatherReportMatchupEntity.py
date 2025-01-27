from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from db.fantasy_sports_db import db
from models.MLBWeatherReportMatchup import DailyMLBWeatherReport

class MLBWeatherReportMatchupEntity(db.Model):
    __tablename__ = 'MLBWeatherReportMatchup'

    Id = mapped_column(Integer, primary_key=True)
    MLBWeatherReportXrefId = mapped_column(ForeignKey('MLBWeatherReport.Id'), nullable=False)
    GameDate = mapped_column(DateTime, nullable=False)
    AwayTeam = mapped_column(String(50), nullable=False)
    HomeTeam = mapped_column(String(50), nullable=False)
    GameDescription = mapped_column(String, nullable=True)
    GameSentiment = mapped_column(String, nullable=True)
    CreatedOn = mapped_column(DateTime, nullable=False)
    UpdatedOn = mapped_column(DateTime, nullable=True)