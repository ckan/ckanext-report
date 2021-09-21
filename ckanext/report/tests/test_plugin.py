import pytest

from ckan.tests import helpers, factories

import ckanext.report.model as report_model

@pytest.fixture
def report_setup():
    report_model.init_tables()

@pytest.mark.ckan_config(u'ckan.plugins', u'report tagless_report')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'report_setup')
class TestReportPlugin(object):

    def test_report_routes(self, app):
        u"""Test report routes"""
        res = app.get(u'/report')

        assert helpers.body_contains(res, u"Reports")

    def test_tagless_report_listed(self, app):
        u"""Test tagless report is listed on report page"""
        res = app.get(u'/report')

        assert helpers.body_contains(res, u'Tagless datasets')
        assert helpers.body_contains(res, u'href="/report/tagless-datasets"')

    def test_tagless_report(self,app):
        u"""Test tagless report generation"""
        dataset = factories.Dataset()

        res = app.get(u'/report/tagless-datasets')

        assert helpers.body_contains(res, u"Datasets which have no tags.")
        assert helpers.body_contains(res, 'href="/dataset/' + dataset['name'] + '"')
