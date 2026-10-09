#!/bin/bash

set -e

sudo yum update -y

sudo yum install docker -y

sudo systemctl start docker

docker network create dashboard_pollution_network
docker network create db_pollution_network
docker network create airflow_apiserver_network

cd caddy
docker compose up -d
cd ..

cd airflow_project_pollution
docker compose up -d
cd ..

cd dashboard
docker compose up -d
cd ..

. ./.env

echo "$AIRFLOW_PASSWORD"

docker exec -e AIRFLOW_PASSWORD=$AIRFLOW_PASSWORD airflow_project_pollution-airflow-apiserver-1 sh -c '
    echo $AIRFLOW_PASSWORD

    airflow users create \
        --username twardy \
        --firstname Patryk \
        --lastname Twardowski \
        --role Admin \
        --email patryktwardowski79@gmail.com \
        --password $AIRFLOW_PASSWORD

     airflow users delete \
        --username airflow
'