import time
from prometheus.prometheus_module import PrometheusClient, PrometheusDaemon

class PrintWithMetric:
    def setup(self):
        self.client = PrometheusClient()
        self.daemon = PrometheusDaemon()
        self.daemon.create_gauge(name="five_div", documentation="Counter for amount of 5-dividend number", labelnames=["success"])
        self.daemon.create_gauge(name="three_div", documentation="Counter for amount of 3-dividend number", labelnames=["success"])
        self.daemon.run()
    
    def teardown(self):
        self.daemon.shutdown()

    def print_all_numbers(self,start:int=1, end:int=200):
        threes = 0
        fives = 0
        for i in range(start, end+1):
            if i%100==0:
                print("At this time i = "+str(i))
                # update metrics here
                self.client.inc_gauge(name="three_div", amount=threes, success=True)
                self.client.inc_gauge(name="five_div", amount=fives, success=True)
                time.sleep(2)
                # reset counters
                threes = 0
                fives = 0
            # TODO: add a log here
            if i%3 == 0:
                threes += 1
            if i%5 == 0:
                fives += 1
        
        self.client.inc_gauge(name="three_div", amount=threes, success=True)
        self.client.inc_gauge(name="five_div", amount=fives, success=True)
        time.sleep(2)
    
if __name__ == "__main__":
    # 1. setup
    instance = PrintWithMetric()
    instance.setup()
    # 2. execute program
    instance.print_all_numbers()
    # 3. get metric
    metric1 = instance.daemon.metric_dict.get("three_div")
    metric2 = instance.daemon.metric_dict.get("five_div")
    print(metric1.collect()[0].samples[0].value)
    print(metric2.collect()[0].samples[0].value)
    time.sleep(2)
    # 4. tear down
    instance.teardown()