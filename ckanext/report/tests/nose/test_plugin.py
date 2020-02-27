import ckan.plugins as plugins
import ckan.tests.helpers as helpers

class TestReportPlugin(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(TestReportPlugin, cls).setup_class()
        if not plugins.plugin_loaded(u'report'):
            plugins.load(u'report')

    @classmethod
    def teardown_class(cls):
        plugins.unload(u'report')
        super(TestReportPlugin, cls).teardown_class()

    def test_report_routes(self):
        u"""Test report routes"""
        app = self._get_test_app()
        res = app.get(u'/report')

        assert helpers.body_contains(res, u"Reports")