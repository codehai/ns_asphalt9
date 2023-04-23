FROM dorowu/ubuntu-desktop-lxde-vnc:focal-arm64

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY etc/sources-arm64.list /etc/apt/sources.list

# RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 4EB27DB2A3B88B8B
RUN apt update && \
    apt install -y bluez bluetooth


RUN rm /etc/nginx/sites-enabled/default
COPY etc/default /etc/nginx/sites-enabled/

EXPOSE 8080
