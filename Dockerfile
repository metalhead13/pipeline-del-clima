FROM apache/airflow:2.10.5-python3.12

USER root
RUN mkdir -p /opt/airflow/data/{raw,staging,processed,bi,quality} /opt/airflow/logs \
    && chown -R airflow:root /opt/airflow
USER airflow

COPY --chown=airflow:root requirements.txt pyproject.toml /opt/airflow/
COPY --chown=airflow:root src /opt/airflow/src
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt \
    && pip install --no-cache-dir --no-deps -e /opt/airflow

COPY --chown=airflow:root config /opt/airflow/config
COPY --chown=airflow:root dags /opt/airflow/dags
ENV PROJECT_ROOT=/opt/airflow \
    PYTHONPATH=/opt/airflow/src \
    PYTHONUNBUFFERED=1
