import ckan.plugins as plugins
import ckan.tests.helpers as helpers

class TestReportPlugin(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(self):
        if not plugins.plugin_loaded(u'report'):
            plugins.load(u'report')

    @classmethod
    def teardown_class(cls):
        plugins.unload(u'report')

    def test_report_routes(self):
        u"""Test report routes"""
        res = self.app.get(u'/report')

        assert helpers.body_contains(res, u"Reports")