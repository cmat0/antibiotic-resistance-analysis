USE antibiotics_data;

ALTER TABLE amr_2020
DROP COLUMN `Total incidence rate per 100000 population`;

ALTER TABLE amr_2024
RENAME COLUMN `Rate per 100000 population resistant bacteraemia infections` to `AMR Burden rate per 100000 population 2024`;

SELECT * FROM amr_2024;

SELECT `20`.Region,`20`.`AMR Burden rate per 100000 population 2020`,`21`.`AMR Burden rate per 100000 population 2021`,`22`.`AMR Burden rate per 100000 population 2022`,`23`.`AMR Burden rate per 100000 population 2023`,`24`.`AMR Burden rate per 100000 population 2024` FROM amr_2020 AS `20`
JOIN amr_2021 AS `21` ON `21`.Region = `20`.Region
JOIN amr_2022 AS `22` ON `22`.Region = `20`.Region
JOIN amr_2023 AS `23` ON `23`.Region = `20`.Region
JOIN amr_2024 AS `24` ON `24`.Region = `20`.Region;