# encoding: utf-8

import logging
import six
import time

from ckan.lib.helpers import json
try:
    from jinja2.exceptions import TemplateNotFound
except ImportError:
    # CKAN 2.8
    from ckan.lib.render import TemplateNotFound
import ckan.plugins.toolkit as t
from ckan.plugins.toolkit import request, url_for

from .lib import make_csv_from_dicts, ensure_data_is_dicts, anonymise_user_names
from .report_registry import Report, ReportRegistry

log = logging.getLogger(__name__)

c = t.c

###############################################################################
#                                  Controller                                 #
###############################################################################


def _get_routing_rule():
    if hasattr(request, 'url_rule'):
        return request.url_rule.rule
    elif hasattr(request, 'environ'):
        return request.environ.get('pylons.routes_dict')


def report_index():
    try:
        reports = t.get_action('report_list')({}, {})
    except t.NotAuthorized:
        return t.abort(401)

    return t.render('report/index.html', extra_vars={'reports': reports})


def report_view(report_name, organization=None, refresh=False):
    try:
        report = t.get_action('report_show')({}, {'id': report_name})
    except t.NotAuthorized:
        return t.abort(401), None
    except t.ObjectNotFound:
        return t.abort(404), None
    except Exception as e:
        log.error("Failed to get report: %s", e)
        raise

    # ensure correct url is being used
    if organization or 'organization' in _get_routing_rule():
        if 'organization' not in report['option_defaults']:
            # org is supplied but is not a valid input for this report
            return t.redirect_to(url_for('report.view', report_name=report_name)), None
    else:
        org = report['option_defaults'].get('organization')
        if org:
            # org is not supplied, but this report has a default value
            return t.redirect_to(url_for('report.org', report_name=report_name, organization=org)), None
    org_in_params = request.params.get('organization')
    if org_in_params:
        # organization should only be in the url - let the param overwrite
        # the url.
        return t.redirect_to(url_for('report.org', report_name=report_name, organization=org_in_params)), None

    # options
    options = Report.add_defaults_to_options(request.params, report['option_defaults'])
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
        refresh = t.asbool(request.params.get('refresh'))
        if 'refresh' in options:
            options.pop('refresh')
    except ValueError:
        refresh = False

    # Refresh the cache if requested
    if t.request.method == 'POST' and not format:
        refresh = True

    if refresh:
        try:
            t.get_action('report_refresh')({}, {'id': report_name, 'options': options})
        except t.NotAuthorized:
            return t.abort(401), None
        # Don't want the refresh=1 in the url once it is done
        if organization:
            return t.redirect_to(url_for('report.org', report_name=report_name, organization=organization)), None
        else:
            return t.redirect_to(url_for('report.view', report_name=report_name)), None

    # Check for any options not allowed by the report
    for key in options:
        if key not in report['option_defaults']:
            return t.abort(400, 'Option not allowed by report: %s' % key), None

    try:
        data, report_date = t.get_action('report_data_get')({}, {'id': report_name, 'options': options})
    except t.ObjectNotFound:
        return t.abort(404), None
    except t.NotAuthorized:
        return t.abort(401), None

    if format and format != 'html':
        ensure_data_is_dicts(data)
        anonymise_user_names(data, organization=options.get('organization'))
        if format == 'csv':
            try:
                key = t.get_action('report_key_get')({}, {'id': report_name, 'options': options})
            except t.NotAuthorized:
                return t.abort(401), None
            filename = 'report_%s.csv' % key
            response_headers = {
                'Content-Type': 'application/csv',
                'Content-Disposition': six.text_type('attachment; filename=%s' % (filename))
            }
            return make_csv_from_dicts(data['table']), response_headers
        elif format == 'json':
            data['generated_at'] = report_date
            return json.dumps(data), {'Content-Type': 'application/json'}
        else:
            return t.abort(400, 'Format not known - try html, json or csv'), None

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
        'are_some_results': are_some_results}), None


###############################################################################
#                                     CLI                                     #
###############################################################################


def initdb():
    from ckanext.report import model
    model.init_tables()


def generate(report_list):
    timings = {}

    registry = ReportRegistry.instance()
    if report_list:
        print(report_list)
        for report_name in report_list:
            s = time.time()
            registry.get_report(report_name).refresh_cache_for_all_options()
            timings[report_name] = time.time() - s
    else:
        s = time.time()
        registry.refresh_cache_for_all_reports()
        timings["All Reports"] = time.time() - s

    return timings


def list_reports():
    registry = ReportRegistry.instance()
    for plugin, report_name, report_title in registry.get_names():
        report = registry.get_report(report_name)
        date = report.get_cached_date()
        print('%s: %s %s' % (plugin, report_name,
              date.strftime('%d/%m/%Y %H:%M') if date else '(not cached)'))


def generate_for_options(report_name, options):
    report_options = {}

    for option_arg in options:
        if '=' not in option_arg:
            return 'Option needs an "=" sign in it: "%s"' % option_arg
        equal_pos = option_arg.find('=')
        key, value = option_arg[:equal_pos], option_arg[equal_pos + 1:]
        if value == '':
            value = None  # this is what the web i/f does with params
        report_options[key] = value

    log.info("Running report => %s", report_name)
    registry = ReportRegistry.instance()
    report = registry.get_report(report_name)
    all_options = report.add_defaults_to_options(report_options,
                                                 report.option_defaults)
    report.refresh_cache(all_options)
