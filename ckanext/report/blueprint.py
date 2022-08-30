# encoding: utf-8

import six

from flask import Blueprint, make_response

from ckan.plugins import toolkit

from .utils import report_index as index, report_view


report = Blueprint(u'report', __name__)


def redirect_to_index():
    return toolkit.redirect_to('/report')


def view(report_name, organization=None, refresh=False):
    body, headers = report_view(report_name, organization, refresh)
    if headers:
        response = make_response(body)
        for key, value in six.iteritems(headers):
            response.headers[key] = value
        return response
    else:
        return body


report.add_url_rule(u'/report', 'index', view_func=index)
report.add_url_rule(u'/reports', 'reports', view_func=redirect_to_index)
report.add_url_rule(u'/report/<report_name>', view_func=view, methods=('GET', 'POST'))
report.add_url_rule(u'/report/<report_name>/<organization>', 'org', view_func=view, methods=('GET', 'POST',))


def get_blueprints():
    return [report]
