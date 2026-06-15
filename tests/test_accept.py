import unittest
from flask import Flask
import flask_restful
from werkzeug import exceptions



class AcceptTestCase(unittest.TestCase):

    def test_accept_default_application_json(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_match_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_default_override_accept(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_default_any_pick_first(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', '*/*')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_no_match_not_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_custom_repr_match(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_custom_repr_not_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_match_q0_not_acceptable(self):
        """
        q=0 should be considered NotAcceptable,
        but this depends on werkzeug >= 1.0 which is not yet released
        so this test is expected to fail until we depend on werkzeug >= 1.0
        """
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'application/json')

    def test_accept_no_default_accept_highest_quality_of_two(self):
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=1.0')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_accept_highest_quality_of_three(self):
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/html')
        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=0.3, text/html; q=0.2')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_no_representations(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'text/plain')

    def test_accept_invalid_default_no_representations(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype='nonexistant/mediatype')
        api.representations = {}

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 500)

    def test_accept_multiple_representations_pick_match(self):
        """When multiple representations are registered, the one matching
        the Accept header should be selected."""

        class Foo(flask_restful.Resource):
            def get(self):
                return {"msg": "hello"}

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        @api.representation('text/html')
        def html_rep(data, status_code, headers=None):
            resp = app.make_response(('<b>{0}</b>'.format(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/html')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/html')

    def test_accept_multiple_representations_wildcard(self):
        """With multiple representations and Accept: */*, the first
        registered representation (application/json) should win."""

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', '*/*')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')

    def test_accept_no_default_406_message_contains_negotiation_detail(self):
        """When a 406 is raised, the response body should contain useful
        negotiation details (requested types, available representations)."""

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 406)
            import json
            body = json.loads(res.data.decode('utf-8'))
            # The message should mention what was requested and what's available
            self.assertIn('application/xml', body['message'])
            self.assertIn('application/json', body['message'])

    def test_accept_invalid_default_500_message_is_descriptive(self):
        """When default_mediatype has no registered representation, the 500
        error message should describe the misconfiguration."""

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype='application/xml')
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/xml')])
            self.assertEqual(res.status_code, 500)

    def test_select_mediatype_returns_detail_for_match(self):
        """_select_mediatype should return a descriptive detail string
        when a representation is matched."""

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        with app.test_request_context('/', headers=[('Accept', 'application/json')]):
            mediatype, detail = api._select_mediatype()
            self.assertEqual(mediatype, 'application/json')
            self.assertIn('matched', detail)
            self.assertIn('application/json', detail)

    def test_select_mediatype_returns_detail_for_no_match(self):
        """_select_mediatype should return None and a helpful detail when
        no acceptable type is found."""

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        with app.test_request_context('/', headers=[('Accept', 'application/xml')]):
            mediatype, detail = api._select_mediatype()
            self.assertIsNone(mediatype)
            self.assertIn('No acceptable media type', detail)
            self.assertIn('application/xml', detail)

    def test_select_mediatype_returns_detail_for_default_fallback(self):
        """_select_mediatype should explain when the default media type
        is used as fallback (not matched from representations)."""

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype='text/plain')
        api.representations = {}

        with app.test_request_context('/', headers=[('Accept', 'text/html')]):
            mediatype, detail = api._select_mediatype()
            self.assertEqual(mediatype, 'text/plain')
            self.assertIn('default', detail)

    def test_select_mediatype_fallback_override(self):
        """The fallback_mediatype parameter should override
        self.default_mediatype."""

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        with app.test_request_context('/', headers=[('Accept', 'text/html')]):
            mediatype, detail = api._select_mediatype(fallback_mediatype='text/plain')
            self.assertEqual(mediatype, 'text/plain')

    def test_accept_text_plain_default_no_representation(self):
        """When default_mediatype is text/plain and it's not a registered
        representation, make_response should still produce a plain text
        response via the built-in fallback."""

        class Foo(flask_restful.Resource):
            def get(self):
                return "hello plain"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype='text/plain')

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')

    def test_accept_custom_repr_overrides_text_plain_builtin(self):
        """If text/plain is registered as a custom representation, that
        representation should be used instead of the built-in str() fallback."""

        class Foo(flask_restful.Resource):
            def get(self):
                return {"key": "value"}

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/plain')
        def custom_text(data, status_code, headers=None):
            resp = app.make_response(('CUSTOM:' + str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')
            self.assertTrue(res.data.decode('utf-8').startswith('CUSTOM:'))

    def test_accept_multiple_repr_partial_match(self):
        """When Accept lists several types but only some are registered,
        the best registered match should be used."""

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/html')
        def html_rep(data, status_code, headers=None):
            resp = app.make_response(('<b>{0}</b>'.format(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            # application/xml is not registered, but text/html is
            res = client.get('/', headers=[('Accept', 'application/xml; q=1.0, text/html; q=0.9')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/html')
