from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Tuple, Union
import prometheus_client as prometheus


class MetricEvent(ABC):
    name: str
    amount: Any
    labels: Dict
    metric_type: Any

    def __init__(self, name: str, amount: Any, metric_type:Any, labels: Dict[str, Any]) -> None:
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

    def update_event(self, metric: prometheus.metrics.Counter) -> None:
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
    metric_dict: Dict[str, Any]
    def __init__(self) -> None:
        self.metric_dict = dict()

    def _create_metric(self, metric_type: Any, name: str, documentation: str, labelnames: List[str], states: Optional[Any]=None) -> None:
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
        self._create_metric(metric_type, name, documentation, labelnames)

    def create_gauge(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Gauge metric
        """
        metric_type = prometheus.Gauge
        self._create_metric(metric_type, name, documentation, labelnames)
    
    def create_summary(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Summary metric
        """
        metric_type = prometheus.Summary
        self._create_metric(metric_type, name, documentation, labelnames)
    
    def create_histogram(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Histogram metric
        """
        metric_type = prometheus.Histogram
        self._create_metric(metric_type, name, documentation, labelnames)
    
    def create_info(self, name: str, documentation: Any, labelnames: List[str]) -> None:
        """
        Creates a Prometheus Info metric
        """
        metric_type = prometheus.Info
        self._create_metric(metric_type, name, documentation, labelnames)

    def create_enum(self, name: str, documentation: Any, labelnames: List[str], states: List[str]) -> None:
        """
        Creates a Prometheus Enum metric
        """
        metric_type = prometheus.Enum
        self._create_metric(metric_type, name, documentation, labelnames, states)
    

if __name__ == "__main__":
    metric = prometheus.metrics.Counter(name="example1", documentation="")
    counter = CounterEvent(name="example2", amount=1, labels={"set": True})

    print(counter.verify_metric_type(metric))

    prometheus_daemon = PrometheusDaemon()
    prometheus_daemon.create_counter(name="total", documentation="none", labelnames=["succeed"])
    print(prometheus_daemon.metric_dict)
    
