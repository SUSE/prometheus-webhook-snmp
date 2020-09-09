FROM opensuse/tumbleweed:latest
MAINTAINER Volker Theile <vtheile@suse.com>

RUN zypper ref && \
    zypper --non-interactive install prometheus-webhook-snmp && \
    zypper clean -a

ENV ARGS=""

CMD exec /usr/bin/prometheus-webhook-snmp --debug run $ARGS
