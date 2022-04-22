import pytest
import six
from ckan.plugins import toolkit as tk
from ckan.tests import factories
import ckanext.report.model as report_model


def _assert_in_body(string, response):
    if six.PY2:
        assert string in response.body.decode('utf8')
    else:
        assert string in response.body


def _assert_status(res, code_int):
    if hasattr(res, 'status_code'):
        assert res.status_code == code_int
    elif hasattr(res, 'status_int'):
        assert res.status_int == code_int
    else:
        raise NotImplementedError('No status for response')


@pytest.fixture
def report_setup():
    report_model.init_tables()


@pytest.mark.ckan_config(u'ckan.plugins', u'report tagless_report')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'report_setup')
class TestReportPlugin(object):

    def test_report_routes(self, app):
        u"""Test report routes"""
        res = app.get(u'/report')

        _assert_in_body(u"Reports", res)

    def test_tagless_report_listed(self, app):
        u"""Test tagless report is listed on report page"""
        res = app.get(u'/report')

        _assert_in_body(u'Tagless datasets', res)
        _assert_in_body(u'href="/report/tagless-datasets"', res)

    def test_tagless_report(self, app):
        u"""Test tagless report generation"""
        dataset = factories.Dataset()

        res = app.get(u'/report/tagless-datasets')

        _assert_in_body(u"Datasets which have no tags.", res)
        _assert_in_body('href="/dataset/' + dataset['name'] + '"', res)

    def test_tagless_report_csv(self, app):
        u"""Test tagless report generation"""
        dataset1 = factories.Dataset()  # noqa F841
        dataset2 = factories.Dataset()  # noqa F841

        res = app.get(u'/report/tagless-datasets?format=csv')
        _assert_status(res, 200)

    def test_tagless_report_json(self, app):
        u"""Test tagless report generation"""
        dataset1 = factories.Dataset()  # noqa F841
        dataset2 = factories.Dataset()  # noqa F841
        res = app.get(u'/report/tagless-datasets?format=json')
        _assert_status(res, 200)

    def test_tagless_report_refresh_ok(self, app):
        u"""Test tagless refresh report"""
        user = factories.Sysadmin()
        dataset = factories.Dataset()  # noqa F841
        env = {'REMOTE_USER': user['name'].encode('ascii')}

        res = app.post('/report/tagless-datasets', extra_environ=env)

        # for CKAN >= 2.9, the response is not a redirect
        if tk.check_ckan_version(min_version="2.9.0"):
            _assert_status(res, 200)
        else:
            _assert_status(res, 302)
            assert res.headers.get('Location') == 'http://localhost:5000/report/tagless-datasets'
