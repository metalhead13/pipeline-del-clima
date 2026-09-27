.PHONY: install test run query init up down clean

install:
	python -m pip install -e .

test:
	pytest

run:
	python -m weather_pipeline.cli run

query:
	python -m weather_pipeline.cli query

init:
	docker compose up airflow-init

up:
	docker compose up --build -d

down:
	docker compose down

clean:
	rm -rf data/raw/extraction_date=* data/staging/*.parquet data/processed/weather_daily data/bi/* data/quality/*.json
