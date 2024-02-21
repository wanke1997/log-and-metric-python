from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import Any, Dict, Optional, List, Union
import prometheus_client as prometheus
from prometheus_client.registry import CollectorRegistry
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
from threading import Thread
from multiprocessing import Queue
from queue import Empty
import logging

metric_event_queue: Queue[MetricEvent] = Queue()


class MetricEvent(ABC):
    name: str
    amount: Any
    labels: Dict
    metric_type: Any

    def __init__(self, name: str, amount: Any, metric_type: Any, labels: Dict[str, Any]) -> None:
        self.name = name
        self.amount = amount
        self.labels = labels
        self.metric_type = metric_type
        super().__init__()

    @abstractmethod
    def update_event(self, metric: Any) -> None:
        pass

    def verify_metric_type(self, metric: prometheus.Metric) -> bool:
        return isinstance(metric, self.metric_type)


class CounterEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Counter
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.Counter) -> None:
        """
        increment counter by the given amount
        """
        metric.labels(**self.labels).inc(self.amount)


class GaugeIncEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Gauge
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Gauge) -> None:
        """
        Increment gauge by the given amount
        """
        metric.labels(**self.labels).inc(self.amount)


class GaugeDecEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Gauge
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Gauge) -> None:
        """
        Decrement gauge by the given amount
        """
        metric.labels(**self.labels).dec(self.amount)


class GaugeSetEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Gauge
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Gauge) -> None:
        """
        Set gauge by the given amount
        """
        metric.labels(**self.labels).set(self.amount)


class SummaryEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Summary
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Summary) -> None:
        """
        Observe the given amount
        """
        metric.labels(**self.labels).observe(self.amount)


class HistogramEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Histogram
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Histogram) -> None:
        """
        Observe the given amount
        """
        metric.labels(**self.labels).observe(self.amount)


class InfoEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Info
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Info) -> None:
        """
        Set info metric
        """
        metric.labels(**self.labels).info(self.amount)


class EnumEvent(MetricEvent):
    def __init__(self, name: str, amount: Any, labels: Dict[str, Any]) -> None:
        metric_type = prometheus.Enum
        super().__init__(name, amount, metric_type, labels)

    def update_event(self, metric: prometheus.metrics.Enum) -> None:
        """
        Set info metric
        """
        metric.labels(**self.labels).state(self.amount)


class PrometheusDaemon:
    metric_dict: Dict[str, prometheus.Metric]
    daemon_thread: bool
    _logger: logging.Logger
    wsgi_server: WSGIServer
    wsgi_server_thread: Thread
    update_event_thread: Thread
    kill_update_event_thread: bool

    def __init__(self) -> None:
        self.metric_dict = dict()
        self.daemon_thread = True
        self.kill_update_event_thread = False
        self._logger = logging.getLogger("basic")
        self._logger.info("Prometheus Daemon initiated")

    def _create_metric_collector(
        self, metric_type: Any, name: str, documentation: str, labelnames: List[str], states: Optional[Any] = None
    ) -> None:
        """
        Base create metric method
        """
        if name in self.metric_dict.keys():
            return
        elif states is not None:
            metric = metric_type(name=name, documentation=documentation, labelnames=labelnames, states=states)
            self.metric_dict[name] = metric
        else:
            metric = metric_type(name=name, documentation=documentation, labelnames=labelnames)
            self.metric_dict[name] = metric

    def create_counter(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Counter metric
        """
        metric_type = prometheus.Counter
        self._create_metric_collector(metric_type, name, documentation, labelnames)

    def create_gauge(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Gauge metric
        """
        metric_type = prometheus.Gauge
        self._create_metric_collector(metric_type, name, documentation, labelnames)

    def create_summary(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Summary metric
        """
        metric_type = prometheus.Summary
        self._create_metric_collector(metric_type, name, documentation, labelnames)

    def create_histogram(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Histogram metric
        """
        metric_type = prometheus.Histogram
        self._create_metric_collector(metric_type, name, documentation, labelnames)

    def create_info(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Info metric
        """
        metric_type = prometheus.Info
        self._create_metric_collector(metric_type, name, documentation, labelnames)

    def create_enum(self, name: str, documentation: Any, labelnames: List[str], states: List[str]) -> None:
        """
        Creates a Prometheus Enum metric
        """
        metric_type = prometheus.Enum
        self._create_metric_collector(metric_type, name, documentation, labelnames, states)

    def remove_metric_collector(self, collector: prometheus.Metric) -> None:
        """
        Removes a metric collectors
        """
        if isinstance(
            collector,
            (
                prometheus.Counter,
                prometheus.Gauge,
                prometheus.Summary,
                prometheus.Histogram,
                prometheus.Info,
                prometheus.Enum,
            ),
        ):
            if collector._name in self.metric_dict:
                self.metric_dict.pop(collector._name)
                prometheus.REGISTRY.unregister(collector)
            else:
                raise Exception("no such collector")

    def run(self, host: str = "0.0.0.0", port: int = 8081, refresh_rate: Union[int, float] = 0.5):
        """
        Start prometheus HTTP server and updating thread
        """
        self._start_server(host, port)
        self.update_event_thread = Thread(target=self._update_metrics, args=(refresh_rate,))
        self.update_event_thread.daemon = True
        self.update_event_thread.start()
        self._logger.info("update_event_thread started")

    def _start_server(self, host: str, port: int, registry: CollectorRegistry = prometheus.REGISTRY):
        """
        Start prometheus HTTP server with wsgi simple httpd server
        """
        # create a wsgi application
        app = prometheus.make_wsgi_app(registry=registry)
        # create a wsgi server instance
        self.wsgi_server = make_server(host, port, app, handler_class=WSGIRequestHandler)
        # launch the server with a thread
        # NOTE: if we set the wsgi_server_thread as a daemon thread, when the main thread terminates, the deamon
        # thread will terminate as well!
        self.wsgi_server_thread = Thread(target=self.wsgi_server.serve_forever, daemon=True)
        self.wsgi_server_thread.start()
        self._logger.info("wsgi_server_thread started")

    def shutdown(self) -> None:
        """
        Shutdown daemon threads
        """
        self.kill_update_event_thread = True
        while self.update_event_thread and self.update_event_thread.is_alive():
            # NOTE: wait until the thread terminates, will not continue until
            # the thread terminates.
            self.update_event_thread.join()
        # closes the wsgi server safely
        self.wsgi_server.shutdown()
        self.wsgi_server.server_close()
        self._logger.info("wsgi_server_thread stopped")

    def _update_metrics(self, refresh_rate: Union[int, float]):
        global metric_event_queue
        while not self.kill_update_event_thread:
            # retrieve an event from metric_event_queue
            try:
                event = metric_event_queue.get_nowait()
            except Empty:
                time.sleep(refresh_rate)
                continue
            name = event.name
            if name in self.metric_dict.keys():
                metric = self.metric_dict.get(name)
                if event.verify_metric_type(metric):
                    event.update_event(metric)
            else:
                self._logger.error("Metric is not the given type")
            time.sleep(refresh_rate)
        self._logger.info("update_event_thread stopped")


class PrometheusClient:
    """
    A Prometheus client which creates metric update events and 
    send them to queue to process
    """

    def _send_to_queue(self, event: MetricEvent) -> None:
        global metric_event_queue
        metric_event_queue.put(event)

    def inc_counter(self, name: str, amount: int, **kwargs: str) -> None:
        event = CounterEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def inc_gauge(self, name: str, amount: int, **kwargs: str) -> None:
        event = GaugeIncEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def dec_gauge(self, name: str, amount: int, **kwargs: str) -> None:
        event = GaugeDecEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def set_gauge(self, name: str, amount: int, **kwargs: str) -> None:
        event = GaugeSetEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def update_summary(self, name: str, amount: int, **kwargs: str) -> None:
        event = SummaryEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def update_histogram(self, name: str, amount: int, **kwargs: str) -> None:
        event = HistogramEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def update_info(self, name: str, amount: int, **kwargs: str) -> None:
        event = InfoEvent(name, amount, kwargs)
        self._send_to_queue(event)

    def update_enum(self, name: str, amount: int, **kwargs: str) -> None:
        event = EnumEvent(name, amount, kwargs)
        self._send_to_queue(event)
