This repository is to implement log and metric system with `structlog` and `Prometheus`. 

### Structure of the project
* `config`: Configuration files are in this directory. Contains `prometheus.yml` mapping to `/etc/prometheus/prometheus.yml` in prometheus-container
* `docker`: Docker files for the project
* `grafana`: Directory for `grafana-container`
* `src`: source code for `driver-container`

### docker image build and launch
```bash
cd docker
docker build -t metric-driver-image -f driver.Dockerfile .
docker-compose up -d
```

### Additional important details for the project
After launching `docker-compose.yml` script, `grafana-container` and `driver-container` started first. After `driver-container` completely started, `prometheus-container` started. The `driver-container` contains a `driver-container:8081` metric endpoint to reflect the prometheus metric. The `prometheus-container` is a prometheus server to gather metric from the metric endpoint and reflect the metric in the `prometheus-container:9090` prometheus server endpoint. The `grafana-container` can read metrics from `prometheus-container:9090` endpoint. <br>

Note that `grafana-container` cannot read `driver-container:8081` metric endpoint directly. It must read metrics from prometheus server's endpoints (`prometheus-container:9090`). <br>

Configuration file for prometheus server is `/etc/prometheus/prometheus.yml` in the container. We set the endpoints in the `scrape_configs` section. 

### reference:
https://medium.com/@e.ahmadi/monitoring-your-system-with-prometheus-and-grafana-efb328cedd4b
https://stackoverflow.com/questions/49829423/prometheus-add-target-specific-label-in-static-configs
https://medium.com/swlh/easy-grafana-and-docker-compose-setup-d0f6f9fcec13
