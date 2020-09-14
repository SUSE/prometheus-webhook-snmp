FROM registry.opensuse.org/opensuse/tumbleweed:latest
MAINTAINER Volker Theile <vtheile@suse.com>

RUN zypper ref && \
    zypper --non-interactive install prometheus-webhook-snmp && \
    zypper clean -a

ENV ARGS="--debug"
ENV RUN_ARGS=""

CMD exec /usr/bin/prometheus-webhook-snmp $ARGS run $RUN_ARGS
