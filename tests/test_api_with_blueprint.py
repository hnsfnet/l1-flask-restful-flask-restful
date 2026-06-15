import unittest
import json
from flask import Flask, Blueprint, request
try:
    from mock import Mock
except:
    # python3
    from unittest.mock import Mock
import flask
import flask_restful
import flask_restful.fields
#noinspection PyUnresolvedReferences
from nose.tools import assert_true, assert_false  # you need it for tests in form of continuations


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}


class GoodbyeWorld(flask_restful.Resource):
    def __init__(self, err):
        self.err = err

    def get(self):
        flask.abort(self.err)


class APIWithBlueprintTestCase(unittest.TestCase):

    def test_api_base(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        self.assertEqual(api.urls, {})
        self.assertEqual(api.prefix, '')
        self.assertEqual(api.default_mediatype, 'application/json')

    def test_api_delayed_initialization(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api()
        api.init_app(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        api.add_resource(HelloWorld, '/', endpoint="hello")

    def test_add_resource_endpoint(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view.as_view.assert_called_with('bar')

    def test_add_resource_endpoint_after_registration(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        view.as_view.assert_called_with('bar')

    def test_url_with_api_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/api/hi'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_url_with_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/hi'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_url_with_registration_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_registration_prefix_overrides_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_url_with_api_and_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/api/hi'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_url_part_order_aeb(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api', url_part_order='aeb')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/api/hi/bp'):
            self.assertEqual(request.endpoint, 'test.hello')

    def test_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/hi', method='POST'):
            assert_true(api._should_use_fr_error_handler())
            assert_true(api._has_fr_route())
        with app.test_request_context('/bye'):
            api._should_use_fr_error_handler = Mock(return_value=False)
            assert_true(api._has_fr_route())

    def test_non_blueprint_rest_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/blueprint')
        api2 = flask_restful.Api(app)
        api2.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api2.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        with app.test_request_context('/hi', method='POST'):
            assert_false(api._should_use_fr_error_handler())
            assert_true(api2._should_use_fr_error_handler())
            assert_false(api._has_fr_route())
            assert_true(api2._has_fr_route())
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert_true(api._should_use_fr_error_handler())
            assert_false(api2._should_use_fr_error_handler())
            assert_true(api._has_fr_route())
            assert_false(api2._has_fr_route())
        api._should_use_fr_error_handler = Mock(return_value=False)
        api2._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert_false(api._has_fr_route())
            assert_true(api2._has_fr_route())
        with app.test_request_context('/blueprint/bye'):
            assert_true(api._has_fr_route())
            assert_false(api2._has_fr_route())

    def test_non_blueprint_non_rest_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/blueprint')

        @app.route('/hi')
        def hi():
            return 'hi'

        @app.route('/bye')
        def bye():
            flask.abort(404)
        with app.test_request_context('/hi', method='POST'):
            assert_false(api._should_use_fr_error_handler())
            assert_false(api._has_fr_route())
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert_true(api._should_use_fr_error_handler())
            assert_true(api._has_fr_route())
        api._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert_false(api._has_fr_route())
        with app.test_request_context('/blueprint/bye'):
            assert_true(api._has_fr_route())

    def test_error_response_formatter_on_blueprint(self):
        """Formatter works when Api is mounted on a Blueprint."""
        def envelope(data, code, headers):
            return {'error': data, 'code': code, 'success': False}

        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, error_response_formatter=envelope)
        api.add_resource(GoodbyeWorld(400), '/fail', endpoint="fail")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/bp')

        client = app.test_client()
        resp = client.get('/bp/fail')
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.data.decode())
        self.assertFalse(body['success'])
        self.assertEqual(body['code'], 400)
        self.assertIn('message', body['error'])

    def test_error_response_formatter_blueprint_does_not_affect_non_blueprint_routes(self):
        """Formatter on a blueprint Api does not affect plain Flask routes."""
        def envelope(data, code, headers):
            return {'error': data, 'code': code}

        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, error_response_formatter=envelope)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/bp')

        @app.route('/plain-404')
        def plain():
            flask.abort(404)

        client = app.test_client()

        # Blueprint route with formatter
        resp = client.get('/bp/hi', method='DELETE')
        self.assertEqual(resp.content_type, 'application/json')

        # Non-blueprint 404 should use Flask's default handler, not the formatter
        resp = client.get('/nonexistent')
        self.assertEqual(resp.status_code, 404)
        content_type, _, _ = resp.headers['Content-Type'].partition(';')
        self.assertEqual('text/html', content_type)

    def test_error_response_formatter_blueprint_500(self):
        """Formatter handles 500 errors in blueprint context."""
        def envelope(data, code, headers):
            return {'error': data, 'code': code}

        class BrokenResource(flask_restful.Resource):
            def get(self):
                raise RuntimeError("something broke")

        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, error_response_formatter=envelope)
        api.add_resource(BrokenResource, '/broken', endpoint="broken")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/bp')

        client = app.test_client()
        resp = client.get('/bp/broken')
        self.assertEqual(resp.status_code, 500)
        body = json.loads(resp.data.decode())
        self.assertEqual(body['code'], 500)
        self.assertIn('message', body['error'])


if __name__ == '__main__':
    unittest.main()
