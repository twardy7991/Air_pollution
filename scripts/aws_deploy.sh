#!/bin/bash

set -e

sudo apt update -y

sudo chown -R "$USER":"$USER" /opt/Air_pollution

sudo apt install python3-pip
pip install torch --index-url https://download.pytorch.org/whl/cpu

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce

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