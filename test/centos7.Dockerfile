FROM centos:7

RUN yum -y install epel-release && \
    yum -y install https://repo.saltstack.com/yum/redhat/salt-repo-latest-1.el7.noarch.rpm && \
    yum clean expire-cache && \
    yum -y install salt-minion
