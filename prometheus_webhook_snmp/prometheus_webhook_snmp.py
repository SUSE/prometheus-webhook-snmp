#!/usr/bin/python3
import datetime
import logging
import sys

import click

from prometheus_webhook_snmp import utils


__version__ = "1.5"


pass_context = click.make_pass_decorator(utils.Context, ensure=True)


@click.group(help='Prometheus Alertmanager receiver that translates '
                  'notifications into SNMP v2c traps.')
@click.option('--debug',
              is_flag=True,
              help='Enable debug output.')
@click.option('--snmp-host',
              help='The host (IPv4, IPv6 or FQDN) of the SNMP trap receiver.')
@click.option('--snmp-port',
              help='The port of the SNMP trap receiver.',
              type=int)
@click.option('--snmp-community',
              help='The SNMP community string.')
@click.option('--snmp-retries',
              help='Maximum number of request retries.',
              type=int)
@click.option('--snmp-timeout',
              help='Response timeout in seconds.',
              type=int)
@click.option('--alert-oid-label',
              help='The label where to find the OID.')
@click.option('--trap-oid-prefix',
              help='The OID prefix for trap variable bindings.')
@click.option('--trap-default-oid',
              help='The trap OID if none is found in the Prometheus alert labels.')
@click.option('--trap-default-severity',
              help='The trap severity if none is found in the Prometheus alert labels.')
@click.version_option(__version__, message="%(version)s")
@pass_context
def cli(ctx, debug, snmp_host, snmp_port, snmp_community, snmp_retries,
        snmp_timeout, alert_oid_label, trap_oid_prefix, trap_default_oid,
        trap_default_severity):
    ctx.config.load(click.get_current_context().info_name)
    ctx.config['debug'] = True if debug else None
    ctx.config['snmp_host'] = snmp_host
    ctx.config['snmp_port'] = snmp_port
    ctx.config['snmp_community'] = snmp_community
    ctx.config['snmp_retries'] = snmp_retries
    ctx.config['snmp_timeout'] = snmp_timeout
    ctx.config['alert_oid_label'] = alert_oid_label
    ctx.config['trap_default_oid'] = trap_default_oid
    ctx.config['trap_default_severity'] = trap_default_severity
    ctx.config['trap_oid_prefix'] = trap_oid_prefix

    if ctx.config['debug']:
        logging.basicConfig(level=logging.DEBUG)

    return 0


@cli.command(name='run', help='Start the HTTP server.')
@click.option('--host',
              help='Host to use.')
@click.option('--port',
              help='Port to listen for Prometheus Alertmanager notifications.',
              type=int)
@click.option('--metrics',
              is_flag=True,
              help='Provide Prometheus metrics from this receiver.')
@pass_context
def run(ctx, host, port, metrics):
    ctx.config['host'] = host
    ctx.config['port'] = port
    ctx.config['metrics'] = True if metrics else None
    ctx.config.dump()
    utils.run_http_server(ctx)
    sys.exit(0)


@cli.command(name='test', help='Trigger a SNMP trap.')
@pass_context
def test(ctx):
    ctx.config.dump()
    trap_data = utils.parse_notification(ctx.config, {
        'receiver': 'bar',
        'status': 'firing',
        'alerts': [{
            'status': 'firing',
            'labels': {
                'alertname': 'load_0',
                'instance': 'localhost:9100',
                'job': 'node-exporter',
                'severity': 'info',
                'foo': 'bar',
                'xyz': 'abc'
            },
            'annotations': {
                'description': 'localhost:9100 of job node-exporter load is over 0!',
                'summary': 'Instance localhost:9100 load is over 0!'
            },
            'startsAt': datetime.datetime.utcnow().isoformat() + 'Z',
            'endsAt': '0001-01-01T00:00:00Z',
            'generatorURL': 'http://foo:9090/graph?...'
        }],
        'groupLabels': {},
        'commonLabels': {},
        'commonAnnotations': {},
        'externalURL': '',
        'version': '4',
        'groupKey': '{}:{}'
    })
    if trap_data is not None:
        for data in trap_data:
            utils.send_snmp_trap(ctx.config, data)
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(cli())  # pylint: disable=no-value-for-parameter
