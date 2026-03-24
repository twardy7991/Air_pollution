\c pollution_db

DROP TABLE IF EXISTS weather;
DROP TABLE IF EXISTS pollution;
DROP TABLE IF EXISTS predictions;

CREATE TABLE pollution (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP NOT NULL,
    pm2_5 INTEGER NOT NULL,
    pm_10 INTEGER NOT NULL
);

CREATE TABLE weather (
    id INTEGER PRIMARY KEY,

    time TIMESTAMP NOT NULL,
    temperature_2m INTEGER NOT NULL,
    relative_humidity_2m INTEGER NOT NULL,
    dew_point_2m INTEGER NOT NULL,
    apparent_temperature INTEGER NOT NULL,
    pressure_msl INTEGER NOT NULL,
    surface_pressure INTEGER NOT NULL,

    cloud_cover INTEGER NOT NULL,
    cloud_cover_low INTEGER NOT NULL,
    cloud_cover_mid INTEGER NOT NULL,
    cloud_cover_high INTEGER NOT NULL,

    wind_speed_10m INTEGER NOT NULL,
    wind_speed_80m INTEGER NOT NULL,
    wind_speed_120m INTEGER NOT NULL,
    wind_speed_180m INTEGER NOT NULL,

    wind_direction_10m INTEGER NOT NULL,
    wind_direction_80m INTEGER NOT NULL,
    wind_direction_120m INTEGER NOT NULL,
    wind_direction_180m INTEGER NOT NULL,

    wind_gusts_10m INTEGER NOT NULL,

    shortwave_radiation INTEGER NOT NULL,
    direct_radiation INTEGER NOT NULL,
    direct_normal_irradiance INTEGER NOT NULL,
    diffuse_radiation INTEGER NOT NULL,
    global_tilted_irradiance INTEGER NOT NULL,

    vapour_pressure_deficit INTEGER NOT NULL,
    cape INTEGER NOT NULL,

    evapotranspiration INTEGER NOT NULL,
    et0_fao_evapotranspiration INTEGER NOT NULL,

    precipitation INTEGER NOT NULL,
    snowfall INTEGER NOT NULL,
    precipitation_probability INTEGER NOT NULL,
    rain INTEGER NOT NULL,
    showers INTEGER NOT NULL,

    weather_code INTEGER NOT NULL,

    snow_depth INTEGER NOT NULL,
    freezing_level_height INTEGER NOT NULL,
    visibility INTEGER NOT NULL,

    soil_temperature_0cm INTEGER NOT NULL,
    soil_temperature_6cm INTEGER NOT NULL,
    soil_temperature_18cm INTEGER NOT NULL,
    soil_temperature_54cm INTEGER NOT NULL,

    soil_moisture_0_to_1cm INTEGER NOT NULL,
    soil_moisture_1_to_3cm INTEGER NOT NULL,
    soil_moisture_3_to_9cm INTEGER NOT NULL,
    soil_moisture_9_to_27cm INTEGER NOT NULL,
    soil_moisture_27_to_81cm INTEGER NOT NULL,

    is_day INTEGER NOT NULL
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    run TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    pm2_5 INTEGER NOT NULL
);

CREATE TABLE official_predictions (
    id SERIAL PRIMARY KEY,
    run TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    pm2_5 INTEGER NOT NULL
);

INSERT INTO predictions (id, run, time, pm2_5) VALUES
(1,  'run_2026-03-23_00:00:01', '2026-03-22 00:00:00', 12),
(2,  'run_2026-03-23_00:00:01', '2026-03-22 01:00:00', 14),
(3,  'run_2026-03-23_00:00:01', '2026-03-22 02:00:00', 13),
(4,  'run_2026-03-23_00:00:01', '2026-03-22 03:00:00', 15),
(5,  'run_2026-03-23_00:00:01', '2026-03-22 04:00:00', 16),
(6,  'run_2026-03-23_00:00:01', '2026-03-22 05:00:00', 18),
(7,  'run_2026-03-23_00:00:01', '2026-03-22 06:00:00', 20),
(8,  'run_2026-03-23_00:00:01', '2026-03-22 07:00:00', 22),
(9,  'run_2026-03-23_00:00:01', '2026-03-22 08:00:00', 25),
(10, 'run_2026-03-23_00:00:01', '2026-03-22 09:00:00', 28),
(11, 'run_2026-03-23_00:00:01', '2026-03-22 10:00:00', 30),
(12, 'run_2026-03-23_00:00:01', '2026-03-22 11:00:00', 32),
(13, 'run_2026-03-23_00:00:01', '2026-03-22 12:00:00', 35),
(14, 'run_2026-03-23_00:00:01', '2026-03-22 13:00:00', 33),
(15, 'run_2026-03-23_00:00:01', '2026-03-22 14:00:00', 31),
(16, 'run_2026-03-23_00:00:01', '2026-03-22 15:00:00', 29),
(17, 'run_2026-03-23_00:00:01', '2026-03-22 16:00:00', 27),
(18, 'run_2026-03-23_00:00:01', '2026-03-22 17:00:00', 26),
(19, 'run_2026-03-23_00:00:01', '2026-03-22 18:00:00', 24),
(20, 'run_2026-03-23_00:00:01', '2026-03-22 19:00:00', 22),
(21, 'run_2026-03-23_00:00:01', '2026-03-22 20:00:00', 20),
(22, 'run_2026-03-23_00:00:01', '2026-03-22 21:00:00', 18),
(23, 'run_2026-03-23_00:00:01', '2026-03-22 22:00:00', 16),
(24, 'run_2026-03-23_00:00:01', '2026-03-22 23:00:00', 14);

INSERT INTO pollution (id, time, pm2_5, pm_10) VALUES
(1,  '2026-03-21 00:00:00', 11, 17),
(2,  '2026-03-21 01:00:00', 12, 18),
(3,  '2026-03-21 02:00:00', 13, 19),
(4,  '2026-03-21 03:00:00', 14, 21),
(5,  '2026-03-21 04:00:00', 15, 23),
(6,  '2026-03-21 05:00:00', 17, 26),
(7,  '2026-03-21 06:00:00', 19, 29),
(8,  '2026-03-21 07:00:00', 21, 32),
(9,  '2026-03-21 08:00:00', 24, 35),
(10, '2026-03-21 09:00:00', 27, 39),
(11, '2026-03-21 10:00:00', 29, 42),
(12, '2026-03-21 11:00:00', 31, 44),
(13, '2026-03-21 12:00:00', 34, 47),
(14, '2026-03-21 13:00:00', 32, 45),
(15, '2026-03-21 14:00:00', 30, 43),
(16, '2026-03-21 15:00:00', 28, 41),
(17, '2026-03-21 16:00:00', 26, 38),
(18, '2026-03-21 17:00:00', 25, 36),
(19, '2026-03-21 18:00:00', 23, 34),
(20, '2026-03-21 19:00:00', 21, 31),
(21, '2026-03-21 20:00:00', 19, 29),
(22, '2026-03-21 21:00:00', 17, 26),
(23, '2026-03-21 22:00:00', 15, 23),
(24, '2026-03-21 23:00:00', 13, 20);
