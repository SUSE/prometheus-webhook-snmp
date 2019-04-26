import datetime
import ipaddress
import json
import logging

import cherrypy
import dateutil.parser
import prometheus_client

from pysnmp import hlapi

logger = logging.getLogger(__name__)


def parse_notification(config, notification):
    """
    :param config: The configuration data.
    :type config: dict
    :param notification:
    :type notification: dict
    :return: Returns a list of alert objects.
    :rtype: list or None
    """
    result = None
    if notification and 'alerts' in notification:
        result = []
        for alert in notification['alerts']:
            starts_at = dateutil.parser.parse(alert['startsAt'])
            if alert['endsAt'] != '0001-01-01T00:00:00Z':
                ends_at = dateutil.parser.parse(alert['endsAt'])
            else:
                ends_at = None

            if alert['status'] == 'firing':
                time = starts_at
            elif alert['status'] == 'resolved':
                time = ends_at
            else:
                time = ends_at or starts_at

            labels = alert['labels']
            annotations = alert['annotations']

            summary = annotations.pop('summary', None)
            description = annotations.pop('description', None)
            timestamp = int(time.replace(tzinfo=datetime.timezone.utc).timestamp())

            result.append({
                'oid': labels.pop(config['alert_oid_label'],
                                  config['trap_default_oid']),
                'status': alert['status'],
                'severity': labels.pop('severity'),
                'instance': labels.pop('instance', 'n/a'),
                'job': labels.pop('job'),
                'description': summary or description,
                'tags': labels,
                'timestamp': timestamp,
                'rawdata': alert
            })
    else:
        # This should never happen. Don't raise an exception because it does not
        # make sense to notify Prometheus Alertmanager about this.
        # raise cherrypy.HTTPError(400, 'No alerts in Prometheus notification payload')
        logger.error('No alerts in Prometheus notification payload: %s',
                     json.dumps(notification))
    return result


def send_snmp_trap(config, trap_data):
    """
    Send a SNMP trap.
    :param config: The configuration data.
    :type config: dict
    :param trap_data:
    """
    oids = {
        'status': '{}.1.1.1'.format(config['trap_oid_prefix']),
        'severity': '{}.1.1.2'.format(config['trap_oid_prefix']),
        'instance': '{}.1.1.3'.format(config['trap_oid_prefix']),
        'job': '{}.1.1.4'.format(config['trap_oid_prefix']),
        'description': '{}.1.1.5'.format(config['trap_oid_prefix']),
        'tags': '{}.1.1.6'.format(config['trap_oid_prefix']),
        'timestamp': '{}.1.1.7'.format(config['trap_oid_prefix']),
        'rawdata': '{}.1.1.8'.format(config['trap_oid_prefix'])
    }

    transport_addr = (config['snmp_host'], config['snmp_port'])

    # Configure the transport target (IPv4 or IPv6).
    try:
        # Will raise an exception if ``snmp_host`` isn't an IPv6 address.
        ipaddress.IPv6Address(config['snmp_host'])
        transport_target = hlapi.Udp6TransportTarget(transport_addr)
    except ValueError:
        transport_target = hlapi.UdpTransportTarget(transport_addr)
    transport_target.retries = config['snmp_retries']
    transport_target.timeout = config['snmp_timeout']

    var_binds = hlapi.NotificationType(hlapi.ObjectIdentity(trap_data['oid']))
    var_binds.addVarBinds(
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['status']),
                         hlapi.OctetString(trap_data['status'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['severity']),
                         hlapi.OctetString(trap_data['severity'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['instance']),
                         hlapi.OctetString(trap_data['instance'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['job']),
                         hlapi.OctetString(trap_data['job'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['description']),
                         hlapi.OctetString(trap_data['description'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['tags']),
                         hlapi.OctetString(json.dumps(trap_data['tags']))),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['timestamp']),
                         hlapi.TimeTicks(trap_data['timestamp'])),
        hlapi.ObjectType(hlapi.ObjectIdentity(oids['rawdata']),
                         hlapi.OctetString(json.dumps(trap_data['rawdata'])))
    )

    error_indication, error_status, error_index, _ = next(
        hlapi.sendNotification(
            hlapi.SnmpEngine(),
            hlapi.CommunityData(config['snmp_community'], mpModel=1),
            transport_target, hlapi.ContextData(), 'trap', var_binds))

    if error_indication:
        logger.error('SNMP trap not sent: %s', error_indication)
    elif error_status:
        logger.error('SNMP trap receiver returned error: %s @%s',
                     error_status, error_index)
    else:
        logger.debug('Sending SNMP trap: %s', trap_data)


def get_http_server_config():
    """
    Get the CherryPy application config.
    :return: The CherryPy application config.
    :rtype: dict
    """
    return {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}


def run_http_server(ctx):
    """
    Run the HTTP server.
    :param ctx: The application context.
    :type ctx: dict
    """
    cherrypy.config.update({
        'environment': 'production',
        'server.socket_host': ctx.config['host'],
        'server.socket_port': ctx.config['port']
    })
    cherrypy.quickstart(Root(ctx), config=get_http_server_config())


class Telemetry:
    def __init__(self):
        self.metrics = {
            'notifications': prometheus_client.Counter(
                'prometheus_webhook_snmp_notifications',
                'Number of processed Prometheus Alertmanager notifications.'),
            'traps': prometheus_client.Counter(
                'prometheus_webhook_snmp_traps',
                'Number of sent SNMP traps.')
        }

    def inc(self, name):
        self.metrics[name].inc()

    def generate(self):
        result = []
        for _, metric in self.metrics.items():
            result.append(prometheus_client.generate_latest(metric).
                          decode('utf-8'))
        return ''.join(result)


class Context:
    def __init__(self):
        self.config = {
            key: None
            for key in [
                'host', 'port', 'metrics', 'snmp_host', 'snmp_port',
                'snmp_community', 'snmp_retries', 'snmp_timeout',
                'alert_oid_label', 'trap_default_oid', 'trap_oid_prefix'
            ]
        }
        self.telemetry = Telemetry()


class Metrics:  # pylint: disable=too-few-public-methods
    exposed = True

    def __init__(self, ctx):
        """
        :param ctx: The application context.
        :type ctx: dict
        """
        self.ctx = ctx

    def GET(self):
        """
        Get Prometheus metrics from this receiver.
        :return: The Prometheus metrics.
        :rtype: str
        """
        if not self.ctx.config['metrics']:
            raise cherrypy.HTTPError(405)

        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return self.ctx.telemetry.generate()


class Root:  # pylint: disable=too-few-public-methods
    exposed = True

    def __init__(self, ctx):
        """
        :param ctx: The application context.
        :type ctx: dict
        """
        self.ctx = ctx
        self.metrics = Metrics(ctx)

    @cherrypy.tools.json_in()
    def POST(self):
        """
        Listen for Prometheus Alertmanager notifications.
        """
        notification = cherrypy.request.json
        logger.debug('Receiving notification: %s', notification)
        self.ctx.telemetry.inc('notifications')
        trap_data = parse_notification(self.ctx.config, notification)
        if trap_data is not None:
            for data in trap_data:
                send_snmp_trap(self.ctx.config, data)
                self.ctx.telemetry.inc('traps')
