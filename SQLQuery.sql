IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE [name] = N'QA_TEST')
    CREATE DATABASE QA_TEST;

use QA_TEST

CREATE TABLE InputData(
    ID int identity(1,1) PRIMARY KEY,
    Age int,
    Sex varchar(255),
    BMI decimal(10,2),
    NumOfChildren int,
	isSmoking varchar(255),
	Region varchar(255),
	Prediction decimal(10,2),
	TimeDate datetime)

CREATE TABLE MonitoringData(
    ID int identity(1,1) PRIMARY KEY,
	totalPred int,
	TimeDate datetime)
