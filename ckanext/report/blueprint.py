# encoding: utf-8
import six
import json
from flask import Blueprint, request, make_response

import ckan.plugins.toolkit as t
from jinja2.exceptions import TemplateNotFound

from ckanext.report.report_registry import Report
from ckanext.report.lib import make_csv_from_dicts, ensure_data_is_dicts, anonymise_user_names


import logging
log = logging.getLogger(__name__)

c = t.c

report = Blueprint(u'report', __name__)

def redirect_to_index():
    return t.redirect_to(t.url_for('report.index'))

def index():
    try:
        reports = t.get_action('report_list')({}, {})
    except t.NotAuthorized:
        t.abort(401)

    return t.render('report/index.html', extra_vars={'reports': reports})


def view(report_name, organization=None, refresh=False):
    try:
        report = t.get_action('report_show')({}, {'id': report_name})
    except t.NotAuthorized:
        t.abort(401)
    except t.ObjectNotFound:
        t.abort(404)

    args = t.request.args
    rule = request.url_rule.rule
    # ensure correct url is being used
    if organization or 'organization' in rule:
        if 'organization' not in report['option_defaults']:
            # org is supplied but is not a valid input for this report
            return t.redirect_to(t.url_for('report.view', report_name=report_name, **args))
    else:
        org = report['option_defaults'].get('organization')
        if org:
            # org is not supplied, but this report has a default value
            return t.redirect_to(t.url_for('report.org', report_name=report_name, organization=org, **args))

    org_in_params = t.request.args.get('organization')
    if org_in_params:
        # organization should only be in the url - let the param overwrite
        # the url.
        # remove organization from form arguments
        args = {k: v for k, v in args.items(multi=True) if k != 'organization'}
        return t.redirect_to(t.url_for('report.org', report_name=report_name, organization=org_in_params, **args))

    elif org_in_params == "":
        # remove empty organization from form arguments
        args = {k: v for k, v in args.items(multi=True) if k != 'organization'}
        return t.redirect_to(t.url_for('report.view', report_name=report_name, **args))

    # options
    options = Report.add_defaults_to_options(t.request.args, report['option_defaults'])
    option_display_params = {}
    if 'format' in options:
        format = options.pop('format')
    else:
        format = None
    if 'organization' in report['option_defaults']:
        options['organization'] = organization
    options_html = {}
    c.options = options  # for legacy genshi snippets
    for option in options:
        if option not in report['option_defaults']:
            # e.g. 'refresh' param
            log.warn('Not displaying report option HTML for param %s as option not recognized')
            continue
        option_display_params = {'value': options[option],
                                 'default': report['option_defaults'][option],
                                 'report_name': report_name}
        try:
            options_html[option] = \
                t.render_snippet('report/option_%s.html' % option,
                                 data=option_display_params)
        except TemplateNotFound:
            log.warn('Not displaying report option HTML for param %s as no template found')
            continue

    # Alternative way to refresh the cache - not in the UI, but is
    # handy for testing
    try:
        refresh = t.asbool(t.request.params.get('refresh'))
        if 'refresh' in options:
            options.pop('refresh')
    except t.ValueError:
        refresh = False

    # Refresh the cache if requested
    if t.request.method == 'POST' and not format:
        refresh = True

    if refresh:
        try:
            t.get_action('report_refresh')({}, {'id': report_name, 'options': options})
        except t.NotAuthorized:
            t.abort(401)
        # Don't want the refresh=1 in the url once it is done
        if organization:
            t.redirect_to(t.url_for('report.org', report_name=report_name, organization=organization))
        else:
            t.redirect_to(t.url_for('report.view', report_name=report_name))

    # Check for any options not allowed by the report
    for key in options:
        if key not in report['option_defaults']:
            t.abort(400, 'Option not allowed by report: %s' % key)

    try:
        data, report_date = t.get_action('report_data_get')({}, {'id': report_name, 'options': options})
    except t.ObjectNotFound:
        t.abort(404)
    except t.NotAuthorized:
        t.abort(401)

    if format and format != 'html':
        ensure_data_is_dicts(data)
        anonymise_user_names(data, organization=options.get('organization'))
        if format == 'csv':
            try:
                key = t.get_action('report_key_get')({}, {'id': report_name, 'options': options})
            except t.NotAuthorized:
                t.abort(401)
            filename = 'report_%s.csv' % key
            response = make_response(make_csv_from_dicts(data['table']))
            response.headers['Content-Type'] = 'application/csv'
            response.headers['Content-Disposition'] = six.text_type('attachment; filename=%s' % (filename))
            return response
        elif format == 'json':
            data['generated_at'] = report_date
            response = make_response(json.dumps(data))
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            t.abort(400, 'Format not known - try html, json or csv')

    are_some_results = bool(data['table'] if 'table' in data
                            else data)
    # A couple of context variables for legacy genshi reports
    c.data = data
    c.options = options
    return t.render('report/view.html', extra_vars={
        'report': report, 'report_name': report_name, 'data': data,
        'report_date': report_date, 'options': options,
        'options_html': options_html,
        'report_template': report['template'],
        'are_some_results': are_some_results})


report.add_url_rule(u'/report', view_func=index)
report.add_url_rule(u'/reports', 'reports', view_func=redirect_to_index)
report.add_url_rule(u'/report/<report_name>', view_func=view, methods=['GET', 'POST'])
report.add_url_rule(u'/report/<report_name>/<organization>', 'org',  view_func=view)


def get_blueprints():
    return [report]
