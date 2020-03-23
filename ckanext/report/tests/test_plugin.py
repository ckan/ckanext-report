import pytest

import ckan.tests.helpers as helpers

@pytest.mark.ckan_config(u'ckan.plugins', u'report tagless_report')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins')
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
