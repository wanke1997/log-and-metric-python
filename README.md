### Project Summary
This repository is to implement log and metric system with `structlog` and `Prometheus`. 

### Structure of the Project
* `config`: Configuration files are in this directory. Contains `prometheus.yml` mapping to `/etc/prometheus/prometheus.yml` in prometheus-container
* `docker`: Docker files for the project
* `grafana`: Directory for `grafana-container`
* `src`: Source code for `driver-container`

### Docker Image Build and Launch
```bash
cd docker
docker build -t metric-driver-image -f driver.Dockerfile .
docker-compose up -d
```

### Additional Important Details for the Project
After launching `docker-compose.yml` script, `grafana-container` and `driver-container` started first. `prometheus-container` started afterwards when `driver-container` completely started. <br>

The `driver-container:8081` endpoint reflects original plain prometheus metric. The `prometheus-container:9090` Prometheus server collects original prometheus metric and reflects itself as an application at `prometheus-container:9090`. The metrics are shown at `prometheus-container:9090/metrics` endpoint. The `grafana-container` reads metrics from `prometheus-container:9090` application. <br>

Note that `grafana-container` cannot read `driver-container:8081` original metric endpoint directly. It can only read prometheus server's application from `prometheus-container:9090`. <br>

Configuration file for prometheus server is `/etc/prometheus/prometheus.yml` in the container. We set the endpoints in the `scrape_configs` section. 

### Reference:
https://medium.com/@e.ahmadi/monitoring-your-system-with-prometheus-and-grafana-efb328cedd4b
https://stackoverflow.com/questions/49829423/prometheus-add-target-specific-label-in-static-configs
https://medium.com/swlh/easy-grafana-and-docker-compose-setup-d0f6f9fcec13
