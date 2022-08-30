# encoding: utf-8

import six

import ckan.plugins.toolkit as t
from .utils import report_index, report_view


class ReportController(t.BaseController):

    def index(self):
        return report_index()

    def view(self, report_name, organization=None, refresh=False):
        body, headers = report_view(report_name, organization, refresh)
        if headers:
            for key, value in six.iteritems(headers):
                t.response.headers[key] = value
        return body
