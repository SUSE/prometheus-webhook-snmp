import json
import cherrypy

from cherrypy.test import helper
from prometheus_webhook_snmp.utils import Context, Root, get_http_server_config


class ServerTestCase(helper.CPWebCase):
    @staticmethod
    def setup_server():
        ctx = Context()
        config = get_http_server_config()
        cherrypy.config.update({'environment': 'test_suite'})
        ServerTestCase.app = cherrypy.tree.mount(Root(ctx), config=config)

    def _request(self, url, method, data=None):
        if not data:
            body = None
            headers = None
        else:
            body = json.dumps(data)
            headers = [('Content-Type', 'application/json'),
                       ('Content-Length', str(len(body)))]
        self.getPage(url, method=method, body=body, headers=headers)

    def _post(self, url, data=None):
        self._request(url, 'POST', data)

    def _get(self, url):
        self._request(url, 'GET')

    def test_post(self):
        self._post('/', data={'alerts': {}})
        self.assertStatus('200 OK')

    def test_get_telemetry_on(self):
        cherrypy.tree.apps[''].root.ctx.config['metrics'] = True
        self._get('/metrics')
        self.assertStatus('200 OK')

    def test_get_telemetry_off(self):
        cherrypy.tree.apps[''].root.ctx.config['metrics'] = False
        self._get('/metrics')
        self.assertStatus('405 Method Not Allowed')
