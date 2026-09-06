CREATE DATABASE antibiotics_data;

USE antibiotics_data;

SET GLOBAL local_infile = 1;

CREATE TABLE consumption_location
(
UKHSA_centre VARCHAR(255),
year INT NOT NULL,
primary_care FLOAT NOT NULL,
secondary_care FLOAT NOT NULL,
total FLOAT NOT NULL
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/CLEAN Consumption Location - ESPAUR-2024-to-2025.csv'
INTO TABLE consumption_location
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(UKHSA_centre, year, primary_care, secondary_care, total);

CREATE TABLE amr_location
(
region VARCHAR(255),
year INT NOT NULL,
amr_raw FLOAT NOT NULL,
amr_per_100000 FLOAT NOT NULL,
infections_raw FLOAT NOT NULL,
infections_per_100000 FLOAT NOT NULL
);

CREATE TABLE amr_location_2020 
(
region VARCHAR(255),
phe_centre VARCHAR(255),
year INT NOT NULL,
amr_per_100000 FLOAT NOT NULL,
incidence_per_100000 FLOAT NOT NULL
);

LOAD DATA INFILE "C:\Users\cmat0\OneDrive\Coding\Antibiotics\CLEAN AMR 2020.csv"
INTO TABLE amr_location_2020
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(region, phe_centre, amr_rate_per_100000,total_incidence_per_100000)
SET year = 2020;

LOAD DATA INFILE "C:\Users\cmat0\OneDrive\Coding\Antibiotics\CLEAN AMR 2021.csv"
INTO TABLE amr_location
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(region, amr_per_100000,infections_raw, infections_per_100000)
SET year = 2021;

SELECT * FROM consumption_location
WHERE year = 2021;