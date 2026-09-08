CREATE DATABASE antibiotics_data;

USE antibiotics_data;

CREATE TABLE consumption_location
(
UKHSA_centre VARCHAR(255),
year INT NOT NULL,
primary_care FLOAT NOT NULL,
secondary_care FLOAT NOT NULL,
total FLOAT NOT NULL
);

SELECT * FROM amr_2024;

ALTER TABLE amr_2024
RENAME COLUMN `Estimated number of resistant bacteraemia infections` to `AMR Total 2024`;

SELECT cons.Region, cons.year, cons.`Total Consumption`, amr.`AMR Total 2024`
FROM consumption_location as cons
JOIN amr_2024 as amr
ON cons.Region = amr.Region
WHERE cons.year = 2023;

SELECT * FROM amr_2023;