docker exec airflow_project_pollution-airflow-apiserver-1 sh -c '
    airflow users delete \
        --username twardy 
'

cd caddy
docker compose down
cd ..

cd airflow_project_pollution
docker compose down
cd ..

cd dashboard
docker compose down
cd ..

docker network rm dashboard_pollution_network db_pollution_network airflow_apiserver_network