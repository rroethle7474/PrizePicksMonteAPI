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