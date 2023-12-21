FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tshark

RUN pip3 install pyshark matplotlib

WORKDIR /plots

COPY . /plots

CMD ["./test.sh"]
