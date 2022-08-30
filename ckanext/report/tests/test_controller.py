# encoding: utf-8

from nose.tools import (assert_in,
                        with_setup)

from ckan.tests import helpers


def _setup_function(self):
    self.app = helpers._get_test_app()


def _get_response_body(response):
    ''' Extract the response body of a Webtest or Flask response as text.
    '''
    if hasattr(response, 'html'):
        return response.html.renderContents()
    elif hasattr(response, 'get_data'):
        return response.get_data(as_text=True)
    else:
        raise Exception("Unrecognised response object: [{}]".format(response))


@with_setup(_setup_function)
class TestController():

    def test_report_index(self):
        response = self.app.get('/report', status=200)
        assert_in('<title>Reports', _get_response_body(response))

    def test_report_view(self):
        response = self.app.get('/report/tagless-datasets', status=200)
        assert_in('<title>Tagless datasets', _get_response_body(response))
