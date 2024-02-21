FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y curl vim iputils-ping wget ssh net-tools python3

# RUN apt-get install -y python3-pip 
RUN apt update && apt install python3-pip -y

RUN pip3 install prometheus_client

EXPOSE 8081

RUN update-alternatives --install "/usr/bin/python" "python" "$(which python3)" 1

WORKDIR /opt/src

CMD ["python3", "/opt/src/driver.py"]