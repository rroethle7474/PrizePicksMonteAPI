from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import mapped_column
from db.fantasy_sports_db import db

class MLBWeatherReportEntity(db.Model):
    __tablename__ = 'MLBWeatherReport'

    Id = mapped_column(Integer, primary_key=True)
    ReportDate = mapped_column(DateTime, nullable=False)
    CreatedOn = mapped_column(DateTime, nullable=False)
    UpdatedOn = mapped_column(DateTime, nullable=True)