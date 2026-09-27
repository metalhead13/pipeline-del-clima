from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="colombia_historical_weather",
    description="Open-Meteo raw -> validación -> Parquet particionado -> dataset BI",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "data-engineering", "retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["open-meteo", "colombia", "parquet"],
)
def colombia_historical_weather():
    @task
    def extract_weather():
        from weather_pipeline.pipeline import stage_extract
        return [str(path) for path in stage_extract()]

    @task
    def validate_raw_data():
        from weather_pipeline.pipeline import stage_validate_raw
        return stage_validate_raw()

    @task
    def transform_weather():
        from weather_pipeline.pipeline import stage_transform
        return str(stage_transform())

    @task
    def load_parquet():
        from weather_pipeline.pipeline import stage_load
        return str(stage_load())

    @task
    def generate_dashboard_dataset():
        from weather_pipeline.pipeline import stage_dashboard
        return [str(path) for path in stage_dashboard()]

    extracted = extract_weather()
    validated = validate_raw_data()
    transformed = transform_weather()
    loaded = load_parquet()
    dashboard = generate_dashboard_dataset()
    extracted >> validated >> transformed >> loaded >> dashboard


colombia_historical_weather()
