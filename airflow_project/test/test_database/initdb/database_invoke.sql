\c test_pollution_db

DROP TABLE IF EXISTS weather;
DROP TABLE IF EXISTS pollution;
DROP TABLE IF EXISTS predictions;

CREATE TABLE pollution (
    id SERIAl PRIMARY KEY,
    time TIMESTAMP UNIQUE NOT NULL,
    pm2_5 INTEGER NOT NULL,
    pm_10 INTEGER NOT NULL
);

CREATE TABLE weather (
    id INTEGER PRIMARY KEY,

    time TIMESTAMP UNIQUE NOT NULL,
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

-- INSERT INTO session_data (
--     Year,
--     Race,
--     LapNumber,
--     Driver,
--     Compound,
--     TyreLife,
--     StartFuel,
--     FCL,
--     LapTime,
--     SpeedI1,
--     SpeedI2,
--     SpeedFL,
--     SumLonAcc,
--     SumLatAcc,
--     MeanLapSpeed
-- )
-- VALUES (
--     2024,
--     'Bahrain',
--     12,
--     'VER',
--     'SOFT',
--     7,
--     32.5,
--     0.0,
--     1234567890,
--     295.4,
--     301.2,
--     312.8,
--     145.73,
--     138.91,
--     201.6
-- );

