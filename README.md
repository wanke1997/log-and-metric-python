This repository is to implement log and metric system with `structlog` and `Prometheus`. 

### docker image build and launch
```bash
cd docker
docker build -t metric-driver-image -f driver.Dockerfile .
docker-compose up -d
```

### reference:
https://medium.com/@e.ahmadi/monitoring-your-system-with-prometheus-and-grafana-efb328cedd4b
