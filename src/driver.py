import structlog
import prometheus_client

def print_all_numbers(start:int=1, end:int=200):
    for i in range(start, end+1):
        if i%10==0:
            print("At this time i = "+str(i))
        # add a log here
        if i%3 == 0:
            # add a metric here
            pass
        if i%5 == 0:
            # add a metric here
            pass
    
if __name__ == "__main__":
    print_all_numbers()