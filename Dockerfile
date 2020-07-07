FROM fedora
MAINTAINER mrunge

USER root

RUN dnf -y update
RUN dnf -y install python3-cherrypy python3-PyYAML python3-pysnmp \
                   python3-dateutil python3-click git \
                   python3-prometheus_client && dnf clean all

RUN git clone https://github.com/SUSE/prometheus-webhook-snmp
RUN mv prometheus-webhook-snmp/prometheus-webhook-snmp /usr/bin
RUN mv prometheus-webhook-snmp/prometheus_webhook_snmp /usr/lib/python3.8/site-packages
RUN rm -rf prometheus-webhook-snmp

ENV SNMP_COMMUNITY="public"
ENV SNMP_PORT="162"
ENV SNMP_HOST="localhost"
ENV SNMP_RETRIES="5"
ENV SNMP_TIMEOUT="1"
ENV ALERT_OID_LABEL="oid"

EXPOSE 9099

COPY prometheus-webhook-snmp /
CMD exec /usr/bin/prometheus-webhook-snmp run --snmp-port=$SNMP_PORT \
  --snmp-host=$SNMP_HOST --snmp-community=$SNMP_COMMUNITY \
  --snmp-timeout=$SNMP_TIMEOUT --snmp-retries=$SNMP_RETRIES \
  --alert-oid-label=$ALERT_OID_LABEL

# buildah build-using-dockerfile -t "mrunge/prometheus-webhook-snmp" .
