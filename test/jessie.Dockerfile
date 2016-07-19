FROM debian:jessie

RUN apt-get update && apt-get -y install wget
RUN wget -O - https://repo.saltstack.com/apt/debian/8/amd64/latest/SALTSTACK-GPG-KEY.pub | apt-key add -
RUN echo "deb http://repo.saltstack.com/apt/debian/8/amd64/latest jessie main" > /etc/apt/sources.list.d/saltstack.list
RUN apt-get update && apt-get -y install salt-minion
