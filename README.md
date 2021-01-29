prometheus-webhook-snmp is a Prometheus Alertmanager receiver that translates incoming notifications into SNMP v2c traps.

# Features

- Independent from specific SNMP OID's
- The SNMP OID's of variable binds can be customized via prefix
- Extract SNMP OID from alert label
- Use a default SNMP OID for all alerts without an OID label
- Export Prometheus metrics from this receiver

# Start the receiver

To start the receiver execute the command:

    $ ./prometheus-webhook-snmp run

# Send a test SNMP trap

If you want to send a test SNMP trap, then simply execute the following command. This can be used to test your command line parameters.

    $ ./prometheus-webhook-snmp test

# Command line parameters
Command line parameters have precedence over global configuration settings.

## Global

### --snmp-host
The host (IPv4, IPv6 or FQDN) of the SNMP trap receiver. Defaults to ``localhost``.

### --snmp-port
The port of the SNMP trap receiver. Defaults to ``162``.

### --snmp-community
The SNMP community string. Defaults to ``public``.

### --snmp-retries
Maximum number of request retries. Defaults to ``5``.

### --snmp-timeout
Response timeout in seconds. Defaults to ``1``.

### --alert-oid-label
The label where to find the OID. Defaults to ``oid``.

Example Prometheus alert rule:

```yaml
groups:
- name: mon
  rules:
  - alert: low monitor quorum count
    expr: sum(ceph_mon_quorum_status) < 3
    labels:
      severity: critical
      type: ceph_default
      oid: 1.3.6.1.4.1.50495.15.1.2.3.1
    annotations:
      description: Monitor count in quorum is low.
```

### --trap-oid-prefix
The OID prefix for trap variable bindings. Defaults to ``1.3.6.1.4.1.50495.15``.

### --trap-default-oid
The trap OID if none is found in the Prometheus alert labels. Defaults to ``1.3.6.1.4.1.50495.15.1.2.1``.

### --trap-default-severity
The trap severity if none is found in the Prometheus alert labels. Defaults to an empty string.

## Command ``run``

### --host
The host to use, defaults to ``localhost``.

### --port
Port to listen for Prometheus Alertmanager notifications. Defaults to ``9099``.

Example Prometheus Alertmanager configuration:

```yaml
receivers:
  - name: 'prometheus-webhook-snmp'
    webhook_configs:
    - url: 'http://localhost:9099'
```

### --metrics
Provide Prometheus metrics from this receiver under the URL ``/metrics``.

Example Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'prometheus-webhook-snmp'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:9099']
```

# Global configuration file
The Prometheus Alertmanager receiver can be configured via configuration file, too.
Command line arguments have precedence over the settings in the configuration file.
The configuration file is written in YAML format. The file will be loaded in the
following order and precedence from ``/etc/prometheus-webhook-snmp.conf`` and the
directory in which the prometheus-webhook-snmp command is located.
Parameters in these files have precedence over default configuration settings.
Please replace hyphens in parameter names with underscores.

Example configuration:

```yaml
debug: True
snmp_retries: 1
snmp_community: private
host: promalertmgr.foo.com
port: 9101
```

# SNMP schema

## Traps

| OID | Description |
| :--- | :--- |
| ``trap-oid-prefix``.1.2.1 | The default trap. This is used if no OID is specified in the alert labels. |
| ``trap-oid-prefix``.1.2.[2...N] | Custom traps. |

## Objects

The following objects are appended as variable binds to a SNMP trap.

| OID | Type | Description |
| :--- | :---: | :--- |
| ``trap-oid-prefix``.1.1.1 | String | The name of the Prometheus alert. |
| ``trap-oid-prefix``.1.1.2 | String | The status of the Prometheus alert. |
| ``trap-oid-prefix``.1.1.3 | String | The severity of the Prometheus alert. |
| ``trap-oid-prefix``.1.1.4 | String | Unique identifier for the Prometheus instance. |
| ``trap-oid-prefix``.1.1.5 | String | The name of the Prometheus job. |
| ``trap-oid-prefix``.1.1.6 | String | The Prometheus alert description field. |
| ``trap-oid-prefix``.1.1.7 | String | Additional Prometheus alert labels as JSON string. |
| ``trap-oid-prefix``.1.1.8 | Unix timestamp | The time when the Prometheus alert occurred. |
| ``trap-oid-prefix``.1.1.9 | String | The raw Prometheus alert as JSON string. |


# Docker

## Pull the container

To get the container image, execute the following command:

    $ docker pull registry.opensuse.org/opensuse/prometheus-webhook-snmp:latest
    $ docker pull registry.opensuse.org/opensuse/prometheus-webhook-snmp:1.4

## Networking

You need to publish the port the Prometheus receiver is listening on by
using the command line argument `--publish <HOST_PORT>:<CONTAINER_PORT>`
when running the container because the port is not exposed automatically
because it is configurable. The default port is `9099`.

Alternatively simply connect the container to the host network by using
the command line argument `--network=host`. Additionally the SNMP host
needs to be configured. Use the container's network gateway to be able
to receive SNMP traps outside the container.

## Run the container

There are two options for configuring the container:

1. Environment variables
2. Configuration file

### Environment variables

Use `ARGS` to set [global options](#global) and `RUN_ARGS` for the
[run command options](#command-run). The environment variable `ARGS`
defaults to `--debug`.

    $ docker run --env ARGS="--debug --snmp-community=foo" --env RUN_ARGS="--metrics" ...

### Configuration file

Use a [configuration file](#global-configuration-file) by mounting it into the container.

    $ docker run -v $(pwd)/prometheus-webhook-snmp.conf:/etc/prometheus-webhook-snmp.conf ...
