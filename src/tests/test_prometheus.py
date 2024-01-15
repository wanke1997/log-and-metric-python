import os
import sys
import unittest
import time
import prometheus_client
from multiprocessing import Process
# The lines below is used to import src directory, then we can import prometheus folder
path = os.getcwd()
path = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(path)
from prometheus.prometheus_module import PrometheusDaemon, PrometheusClient, metric_event_queue

class PrometheusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "0.0.0.0"
        cls.port = 8092
        cls.prometheus_daemon = PrometheusDaemon()
        cls.client = PrometheusClient()
        cls.prometheus_daemon.run(host=cls.host, port=cls.port)
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.prometheus_daemon.shutdown()
        cls.prometheus_daemon.wsgi_server_thread.join()
        cls.prometheus_daemon.update_event_thread.join()
    
    def test_metric(self):
        # 1. create metric collectors
        self.prometheus_daemon.create_counter(name="total", documentation="none", labelnames=["succeed"])
        self.prometheus_daemon.create_gauge(name="sec", documentation="none", labelnames=["succeed"])
        # 2. modify metrics
        self.client.inc_counter(name="total", amount=1, succeed=True)
        self.client.inc_counter(name="total", amount=24, succeed=True)
        self.client.dec_gauge(name="sec", amount=2, succeed=True)
        # 3. wait for threads to finish tasks
        time.sleep(2)
        # 4. assertions
        metric1 = self.prometheus_daemon.metric_dict.get("total")
        metric2 = self.prometheus_daemon.metric_dict.get("sec")

        assert isinstance(metric1, prometheus_client.Counter)
        assert isinstance(metric2, prometheus_client.Gauge)

        assert float(metric1.collect()[0].samples[0].value) == 25.0
        assert float(metric2.collect()[0].samples[0].value) == -2.0

if __name__ == '__main__':
    unittest.main()