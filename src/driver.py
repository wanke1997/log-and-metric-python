import time
import logging
from logging import StreamHandler
from prometheus.prometheus_module import PrometheusClient, PrometheusDaemon
import ecs_logging
import os
import shutil

LOG_DIR = "/usr/share/logs/"

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
    logger = logging.getLogger("basic")
    logger.setLevel(level=logging.INFO)
    os.mkdir("logs")
    ecs_handler = logging.FileHandler(LOG_DIR+"driver_log.json")
    ecs_handler.setFormatter(ecs_logging.StdlibFormatter())
    logger.addHandler(ecs_handler)
    if not logger.handlers:
        hdlr = StreamHandler()
        hdlr.setLevel(level=logging.INFO)
        json_format = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
        hdlr.setFormatter(json_format)
        logger.addHandler(hdlr=hdlr)
    else:
        json_format = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
        hdlr2 = StreamHandler()
        hdlr2.setLevel(level=logging.INFO)
        hdlr2.setFormatter(json_format)
        logger.addHandler(hdlr=hdlr2)
    logger.info("Setup finished for the driver code")
    instance = PrintWithMetric()
    instance.setup()
    # 2. execute program
    instance.print_all_numbers()
    # 3. get metric
    metric1 = instance.daemon.metric_dict.get("three_div")
    metric2 = instance.daemon.metric_dict.get("five_div")
    print(metric1.collect()[0].samples[0].value)
    print(metric2.collect()[0].samples[0].value)
    
    # while True:
    #     time.sleep(10)
    # time.sleep(5*60)
    # 4. tear down
    instance.teardown()