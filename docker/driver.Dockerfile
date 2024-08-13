FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y curl vim iputils-ping wget ssh net-tools python3

# RUN apt-get install -y python3-pip 
RUN apt-get update && apt-get install python3-pip -y

RUN pip3 install --break-system-packages prometheus_client ecs_logging

EXPOSE 8081

RUN update-alternatives --install "/usr/bin/python" "python" "$(which python3)" 1

WORKDIR /opt/src

CMD ["python3", "/opt/src/driver.py"]