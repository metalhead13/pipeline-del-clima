-- Ejecutar con DuckDB desde la raíz del proyecto.
CREATE OR REPLACE VIEW weather_daily AS
SELECT *
FROM read_parquet('data/processed/weather_daily/**/*.parquet', hive_partitioning = true);

-- Comparación general por ciudad.
SELECT city_name,
       round(avg(temperature_mean_c), 2) AS avg_temperature_c,
       round(sum(precipitation_sum_mm), 2) AS total_precipitation_mm,
       sum(is_adverse_day::INTEGER) AS adverse_days
FROM weather_daily
GROUP BY city_name
ORDER BY total_precipitation_mm DESC;

-- Evolución mensual preparada para BI.
SELECT *
FROM read_parquet('data/bi/weather_monthly.parquet')
ORDER BY period, city;
