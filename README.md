### Project Summary
This repository is to implement log and metric system with `structlog` and `Prometheus`. 

### Structure of the Project
* `config`: Configuration files are in this directory. `prometheus.yml` maps to `/etc/prometheus/prometheus.yml` for prometheus-container. `filebeat.yml` maps to `/usr/share/filebeat/filebeat.yml` for filebeat-container. 
* `docker`: Docker files for the project
* `grafana`: Directory for `grafana-container`
* `src`: Source code for `driver-container`
* `logs`: The driver code may create `logs` directory to store logs as .json format. 

### Docker Image Build and Launch
```bash
sudo chmod -R 444 config
cd docker
docker build -t metric-driver-image -f driver.Dockerfile .
docker-compose up -d
```

### Endpoints
All URLs are shown in the table below. Note that all hostnames are mapped to `localhost`.
| URL    | Description |
| -------- | ------- |
| driver-container:8081  | Original prometheus metric    |
| prometheus-container:9090 | Prometheus server application    |
| grafana-container:3000    | Grafana page    |
| kibana:5601    | Kibana application    |

### Unit Test Script
```bash
cd src/tests/
python test_prometheus.py
```

### Additional Important Details for the Project
After launching `docker-compose.yml` script, `grafana-container` and `driver-container` started first. `prometheus-container` started afterwards when `driver-container` completely started. <br>

The `driver-container:8081` endpoint reflects original plain prometheus metric. The Prometheus server scrapes original prometheus metric and exposes itself as a service at `prometheus-container:9090`. The metrics are shown at `prometheus-container:9090/metrics` endpoint. The `grafana-container` reads metrics from `prometheus-container:9090` service. <br>

Note that `grafana-container` cannot read `driver-container:8081` original metric endpoint directly. It can only read prometheus server's service from `prometheus-container:9090`. <br>

Configuration file for prometheus server is `/etc/prometheus/prometheus.yml` in the container. We set the endpoints in the `scrape_configs` section. 

### Reference:
https://medium.com/@e.ahmadi/monitoring-your-system-with-prometheus-and-grafana-efb328cedd4b
https://stackoverflow.com/questions/49829423/prometheus-add-target-specific-label-in-static-configs
https://medium.com/swlh/easy-grafana-and-docker-compose-setup-d0f6f9fcec13
https://stackoverflow.com/questions/70586927/how-to-add-the-kafka-exporter-as-a-data-source-to-grafana
https://www.elastic.co/guide/en/cloud/current/ec-getting-started-search-use-cases-python-logs.html
