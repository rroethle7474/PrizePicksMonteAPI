# PrizePicksMonteCarloSimulator API

## Project Description
The PrizePicksMonteCarloSimulator API is a Flask-based application that performs Monte Carlo simulations for sports betting strategies. It specializes in simulating and evaluating different betting strategies for Prize Picks betting options with a focus on MLB (Major League Baseball). The API provides endpoints for running simulations, calculating win probabilities, and retrieving sports data including MLB game information, starting lineups, and weather reports that can impact game outcomes.

## Technologies and Packages Used

### Core Technologies
- **Python** - The primary programming language
- **Flask** - Web framework for building the API
- **SQLAlchemy** - ORM for database interactions
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **Flask-Caching** - Caching mechanism to improve performance

### Key Packages
- **NumPy** - For numerical computations in the Monte Carlo simulations
- **Requests** - For making HTTP requests to external APIs
- **BeautifulSoup** - For web scraping MLB data
- **Statistics** - For statistical calculations on simulation results

### External APIs
- **RapidAPI Baseball API** - For retrieving MLB game data
- **MLB.com** - Web scraping for starting lineups
- **Rotowire** - Web scraping for weather reports

## Routes and Services

### Simulation Routes
- **POST /simulatesingle** - Runs a single simulation for all bet options
- **POST /simulate** - Runs multiple trials of Monte Carlo simulations

### MLB Data Routes
- **GET /win_prob/[min_at_bats]/[max_at_bats]** - Calculates winning probabilities for a player
- **GET /get_yesterday_games/** - Retrieves game IDs from yesterday
- **GET /getmlbgames** - Retrieves current MLB game data
- **GET /getmlbstartinglineups** - Retrieves starting lineups for MLB games
- **GET /getmlbdailyweather** - Retrieves daily weather reports for MLB games
- **GET /langchain** - Experimental route for RAG (Retrieval Augmented Generation)

### Services
- **ProbabilityService** - Calculates winning probabilities based on player statistics
- **ScheduleService** - Retrieves and processes game schedule information
- **WeatherService** - Fetches and processes weather data for games
- **LoggingService** - Handles application logging

## Database Configuration

The application uses SQLAlchemy as an ORM with the following configuration: (current app uses SQL through SSMS locally)

```python
app.config['SQLALCHEMY_DATABASE_URI'] = r''  # Connection string needs to be configured
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```
The authentication on my local machine is using version 18 (ODBC) and Windows Authentication to login to SSMS database.

### Database Considerations
1. **The database must be created manually** - The application does not automatically create the database on startup
2. The connection string needs to be properly configured before use
3. The application supports both ODBC Driver 17 and 18 for SQL Server connections
4. For Driver 17: Use `Trusted_Connection=yes`
5. For Driver 18: Use `TrustServerCertificate=true`
6. Once a proper connection string is provided and the database exists, SQLAlchemy will handle the table structure
7. The database models are stored in the models directory and include entities for:
   - Bet options and winning bets
   - Trial results and final results
   - Player information (pitchers, batters)
   - Team information
   - Weather reports

### Database Initialization
A SQL initialization script is provided to help set up the database:

1. Open SQL Server Management Studio (SSMS)
2. Connect to your local SQL Server instance
3. Open the script located at `sql/initialize_database.sql`
4. Execute the script to create the database and required tables
5. The script creates:
   - A database named `FantasySportsDB`
   - Tables for storing MLB weather reports and related data

## Cache Configuration

The application implements a simple caching mechanism to improve performance:

```python
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 14400  # 4 hours in seconds
```

## Setup Instructions

1. Ensure you have Python 3.6+ installed
2. Install required packages: `pip install -r requirements.txt`
3. Set up the database:
   - Run the initialization script (`sql/initialize_database.sql`) in SQL Server Management Studio
   - Alternatively, create the database and tables manually according to the entity models
4. Configure the database connection string in app.py:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://username:password@server/FantasySportsDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
   ```
   Or for Windows authentication:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://@SERVERNAME\INSTANCENAME/FantasySportsDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
   ```
5. Set up API keys for external services (RapidAPI)
6. Run the application: `python app.py`

## Future Improvements

1. Move configuration to environment variables or a dedicated config file
2. Implement more robust error handling
3. Add authentication for API endpoints
4. Expand simulation options and betting strategies
5. Improve data retrieval mechanisms to reduce dependency on web scraping
6. Implement more comprehensive logging and monitoring

## Initialize Database script
-- Initialize Fantasy Sports Database for PrizePicksMonteCarloSimulator
-- This script creates the database and tables needed for the application

-- Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'FantasySportsDB')
BEGIN
    CREATE DATABASE FantasySportsDB;
END
GO

USE FantasySportsDB;
GO

-- Create MLBWeatherReport table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MLBWeatherReport]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MLBWeatherReport](
        [Id] [int] IDENTITY(1,1) NOT NULL,
        [ReportDate] [datetime] NOT NULL,
        [CreatedOn] [datetime] NOT NULL,
        [UpdatedOn] [datetime] NULL,
        CONSTRAINT [PK_MLBWeatherReport] PRIMARY KEY CLUSTERED ([Id] ASC)
    );
END
GO

-- Create MLBWeatherReportMatchup table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MLBWeatherReportMatchup]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MLBWeatherReportMatchup](
        [Id] [int] IDENTITY(1,1) NOT NULL,
        [MLBWeatherReportXrefId] [int] NOT NULL,
        [GameDate] [datetime] NOT NULL,
        [AwayTeam] [nvarchar](50) NOT NULL,
        [HomeTeam] [nvarchar](50) NOT NULL,
        [GameDescription] [nvarchar](max) NULL,
        [GameSentiment] [nvarchar](max) NULL,
        [CreatedOn] [datetime] NOT NULL,
        [UpdatedOn] [datetime] NULL,
        CONSTRAINT [PK_MLBWeatherReportMatchup] PRIMARY KEY CLUSTERED ([Id] ASC)
    );
END
GO

-- Add foreign key constraint
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK_MLBWeatherReportMatchup_MLBWeatherReport]') 
  AND parent_object_id = OBJECT_ID(N'[dbo].[MLBWeatherReportMatchup]'))
BEGIN
    ALTER TABLE [dbo].[MLBWeatherReportMatchup] 
    ADD CONSTRAINT [FK_MLBWeatherReportMatchup_MLBWeatherReport] 
    FOREIGN KEY([MLBWeatherReportXrefId]) REFERENCES [dbo].[MLBWeatherReport] ([Id]);
END
GO

PRINT 'Database and tables created successfully.';
GO
