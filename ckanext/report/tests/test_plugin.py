import pytest
import six

from ckan.tests import helpers, factories

import ckanext.report.model as report_model

def _assert_in_body(string, response):
    if six.PY2:
        assert string in response.body.decode('utf8')
    else:
        assert string in response.body

@pytest.fixture
def report_setup():
    report_model.init_tables()


@pytest.mark.ckan_config(u'ckan.plugins', u'report tagless_report')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'report_setup')
class TestReportPlugin(object):

    def test_report_routes(self, app):
        u"""Test report routes"""
        res = app.get(u'/report')

        assert _assert_in_body(u"Reports", res)

    def test_tagless_report_listed(self, app):
        u"""Test tagless report is listed on report page"""
        res = app.get(u'/report')

        assert _assert_in_body(u'Tagless datasets', res)
        assert _assert_in_body(u'href="/report/tagless-datasets"', res)

    def test_tagless_report(self, app):
        u"""Test tagless report generation"""
        dataset = factories.Dataset()

        res = app.get(u'/report/tagless-datasets')

        assert _assert_in_body(u"Datasets which have no tags.", res)
        assert _assert_in_body('href="/dataset/' + dataset['name'] + '"', res)
