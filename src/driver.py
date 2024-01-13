import structlog
import prometheus_client

def print_all_numbers(start:int, end:int):
    for i in range(start, end+1):
        print(i)
        # add a log here
        if i%3 == 0:
            # add a metric here
            pass
        if i%5 == 0:
            # add a metric here
            pass