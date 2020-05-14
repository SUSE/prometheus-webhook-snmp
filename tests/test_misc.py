import unittest
import mock

from pyfakefs import fake_filesystem

from prometheus_webhook_snmp.utils import parse_notification, Config, \
    send_snmp_trap

NOTIFICATION_FIRING = {
    'receiver': 'test-01',
    'status': 'firing',
    'alerts': [{
        'status': 'firing',
        'labels': {
            'alertname': 'load_1',
            'job': 'node-exporter',
            'severity': 'warning',
            'oid': '1.3.6.1.4.1.50495.15.1.2.2'
        },
        'annotations': {
            'description': 'aaa'
        },
        'startsAt': '2019-04-02T17:29:05.244307923Z',
        'endsAt': '0001-01-01T00:00:00Z',
        'generatorURL': 'http://arrakis:9090/graph?g0.expr=node_load1+%3E+0&g0.tab=1'
    }],
    'groupLabels': {},
    'commonLabels': {
        'instance': 'localhost:9100',
        'job': 'node-exporter',
        'severity': 'warning'
    },
    'commonAnnotations': {},
    'externalURL': 'http://arrakis:9093',
    'version': '4',
    'groupKey': '{}:{}'
}
NOTIFICATION_RESOLVED = {  # pylint: disable=line-too-long
    'receiver': 'test-02',
    'status': 'resolved',
    'alerts': [{
        'status': 'resolved',
        'labels': {
            'alertname': 'load_2',
            'instance': 'localhost:9100',
            'job': 'node-exporter',
            'severity': 'critical',
            'foo': 'abc',
            'bar': 123
        },
        'annotations': {
            'description': 'aaa',
            'summary': 'bbb'
        },
        'startsAt': '2019-04-01T09:17:46.646300974Z',
        'endsAt': '2019-04-01T09:19:47.126304527Z',
        'generatorURL': 'http://arrakis:9090/graph?g0.expr=node_load1+%3E+2+'
                        'and+node_load1+%3E+4&g0.tab=1'
    }],
    'groupLabels': {},
    'commonLabels': {
        'instance': 'localhost:9100',
        'job': 'node-exporter',
        'severity': 'warning'
    },
    'commonAnnotations': {},
    'externalURL': 'http://arrakis:9093',
    'version': '4',
    'groupKey': '{}:{}'
}


class FunctionTestCase(unittest.TestCase):
    def test_parse_notification_none(self):
        trap_data = parse_notification({}, {
            'alertsss': {}
        })
        self.assertIsNone(trap_data)

    def test_parse_notification(self):
        trap_data = parse_notification({
            'alert_oid_label': 'oid',
            'trap_default_oid': '1.2.3.4',
            'trap_default_severity': ''
        }, NOTIFICATION_FIRING)
        self.assertIsInstance(trap_data, list)
        trap_data = trap_data[0]
        self.assertEqual(trap_data['oid'], '1.3.6.1.4.1.50495.15.1.2.2')
        self.assertEqual(trap_data['alertname'], 'load_1')
        self.assertEqual(trap_data['status'], 'firing')
        self.assertEqual(trap_data['severity'], 'warning')
        self.assertIsNone(trap_data['instance'])
        self.assertEqual(trap_data['job'], 'node-exporter')
        self.assertEqual(trap_data['description'], 'aaa')
        self.assertIsInstance(trap_data['labels'], dict)
        self.assertEqual(trap_data['labels'], {})
        self.assertEqual(trap_data['timestamp'], 1554226145)
        self.assertIsInstance(trap_data['rawdata'], dict)

    def test_parse_notification_no_oid(self):
        trap_data = parse_notification({
            'alert_oid_label': 'oid',
            'trap_default_oid': '1.2.3.4',
            'trap_default_severity': ''
        }, NOTIFICATION_RESOLVED)
        self.assertIsInstance(trap_data, list)
        trap_data = trap_data[0]
        self.assertEqual(trap_data['oid'], '1.2.3.4')
        self.assertEqual(trap_data['alertname'], 'load_2')
        self.assertEqual(trap_data['status'], 'resolved')
        self.assertEqual(trap_data['severity'], 'critical')
        self.assertEqual(trap_data['instance'], 'localhost:9100')
        self.assertEqual(trap_data['job'], 'node-exporter')
        self.assertEqual(trap_data['description'], 'bbb')
        self.assertIsInstance(trap_data['labels'], dict)
        self.assertEqual(trap_data['labels'], {'foo': 'abc', 'bar': 123})
        self.assertEqual(trap_data['timestamp'], 1554110387)
        self.assertIsInstance(trap_data['rawdata'], dict)

    def test_send_snmp_trap(self):
        config = Config()
        self.assertIsInstance(config['trap_default_severity'], str)
        send_snmp_trap(config, {
            'oid': '1.3.6.1.4.1.50495.15.1.2.1',
            'alertname': None,
            'status': 'resolved',
            'severity': config['trap_default_severity'],
            'instance': None,
            'job': None,
            'description': None,
            'labels': {},
            'timestamp': 1554110387,
            'rawdata': {}
        })


class ConfigTestCase(unittest.TestCase):
    fs = fake_filesystem.FakeFilesystem()
    f_open = fake_filesystem.FakeFileOpen(fs)

    def test_defaults(self):
        self.assertIsInstance(Config.defaults(), dict)

    def test_reset(self):
        config = Config()
        config['snmp_community'] = 'private'
        config.reset('snmp_community')
        self.assertEqual(config['snmp_community'], Config.defaults()['snmp_community'])

    def test_reset_all(self):
        config = Config()
        config['foo'] = 'bar'
        config.reset()
        self.assertDictEqual(config, Config.defaults())

    @mock.patch('builtins.open', new=f_open)
    def test_load(self):
        self.fs.create_file('/etc/abc.conf', contents='''foo: bar\n''')
        config = Config()
        config.load('abc')
        self.assertEqual(config['foo'], 'bar')
