import ckan.plugins as plugins
from ckan.tests import helpers, factories
from ckanext.report import model as report_model

class TestReportPlugin(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(TestReportPlugin, cls).setup_class()
        if not plugins.plugin_loaded(u'report'):
            plugins.load(u'report')
        if not plugins.plugin_loaded(u'tagless_report'):
            plugins.load(u'tagless_report')

        report_model.init_tables()

    @classmethod
    def teardown_class(cls):
        if plugins.plugin_loaded(u'report'):
            plugins.unload(u'report')
        if plugins.plugin_loaded(u'tagless_report'):
            plugins.unload(u'tagless_report')
        super(TestReportPlugin, cls).teardown_class()

    def test_report_routes(self):
        u"""Test report routes"""
        app = self._get_test_app()
        res = app.get(u'/report')

        assert "Reports" in res.body

    def test_tagless_report_listed(self):
        u"""Test tagless report is listed on report page"""
        app = self._get_test_app()
        res = app.get(u'/report')

        assert 'href="/report/tagless-datasets"' in res.body

    def test_tagless_report(self):
        u"""Test tagless report generation"""
        dataset = factories.Dataset()

        app = self._get_test_app()
        res = app.get(u'/report/tagless-datasets')

        assert "Datasets which have no tags." in res.body
        assert 'href="/dataset/' + dataset['name'] + '"' in res.body
