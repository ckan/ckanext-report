import datetime

from ckan.lib.helpers import json
import ckan.plugins.toolkit as t
import ckanext.report.helpers as helpers
from ckanext.report.report_registry import ReportRegistry
from ckan.lib.render import TemplateNotFound
from ckanext.report.json_utils import DateTimeJsonEncoder
from ckan.common import OrderedDict
from ckan import model

c = t.c


class ReportController(t.BaseController):

    def index(self):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user}

        if t.check_access('report_list', context):
            reports = t.get_action('report_list')()
            print "REPORTS = ", reports
            return t.render('report/index.html', extra_vars={'reports': reports})
        else:
            t.abort(401)

    def view(self, report_name, organization=None, refresh=False):
        try:
            report = ReportRegistry.instance().get_report(report_name)
        except KeyError:
            t.abort(404, 'Report not found')

        # ensure correct url is being used
        if 'organization' in t.request.environ['pylons.routes_dict'] and \
            'organization' not in report.option_defaults:
                t.redirect_to(helpers.relative_url_for(organization=None))
        elif 'organization' not in t.request.environ['pylons.routes_dict'] and\
            'organization' in report.option_defaults and \
            report.option_defaults['organization']:
                org = report.option_defaults['organization']
                t.redirect_to(helpers.relative_url_for(organization=org))
        if 'organization' in t.request.params:
            # organization should only be in the url - let the param overwrite
            # the url.
            t.redirect_to(helpers.relative_url_for())

        # options
        options = report.add_defaults_to_options(t.request.params)
        option_display_params = {}
        if 'format' in options:
            format = options.pop('format')
        else:
            format = None
        if 'organization' in report.option_defaults:
            options['organization'] = organization
        options_html = {}
        c.options = options  # for legacy genshi snippets
        for option in options:
            option_display_params = {'value': options[option],
                                     'default': report.option_defaults[option]}
            try:
                options_html[option] = \
                    t.render_snippet('report/option_%s.html' % option,
                                     data=option_display_params)
            except TemplateNotFound:
                continue

        # Refresh the cache if requested
        if t.request.method == 'POST' and not format:
            if not (c.userobj and c.userobj.sysadmin):
                t.abort(401)
            report.refresh_cache(options)

        # Alternative way to refresh the cache - not in the UI, but is
        # handy for testing
        try:
            refresh = t.asbool(t.request.params.get('refresh'))
        except ValueError:
            refresh = False
        if refresh:
            if not (c.userobj and c.userobj.sysadmin):
                t.abort(401)
            options.pop('refresh')
            report.refresh_cache(options)
            # Don't want the refresh=1 in the url once it is done
            t.redirect_to(helpers.relative_url_for(refresh=None))

        # Check for any options not allowed by the report
        for key in options:
            if key not in report.option_defaults:
                t.abort(400, 'Option not allowed by report: %s' % key)

        try:
            data, report_date = report.get_fresh_report(**options)
        except t.ObjectNotFound:
            t.abort(404)

        if format and format != 'html':
            ensure_data_is_dicts(data)
            anonymise_user_names(data, organization=options.get('organization'))
            if format == 'csv':
                filename = 'report_%s.csv' % report.generate_key(options).replace('?', '_')
                t.response.headers['Content-Type'] = 'application/csv'
                t.response.headers['Content-Disposition'] = str('attachment; filename=%s' % (filename))
                return make_csv_from_dicts(data['table'])
            elif format == 'json':
                t.response.headers['Content-Type'] = 'application/json'
                data['generated_at'] = report_date
                return json.dumps(data, cls=DateTimeJsonEncoder)
            else:
                t.abort(400, 'Format not known - try html, json or csv')

        are_some_results = bool(data['table'] if 'table' in data
                                else data)
        report_template = report.get_template()
        # A couple of context variables for legacy genshi reports
        c.data = data
        c.options = options
        return t.render('report/view.html', extra_vars={
            'report': report, 'report_name': report_name, 'data': data,
            'report_date': report_date, 'options': options,
            'options_html': options_html,
            'report_template': report_template,
            'are_some_results': are_some_results})


def make_csv_from_dicts(rows):
    import csv
    import cStringIO as StringIO

    csvout = StringIO.StringIO()
    csvwriter = csv.writer(
        csvout,
        dialect='excel',
        quoting=csv.QUOTE_NONNUMERIC
    )
    # extract the headers by looking at all the rows and
    # get a full list of the keys, retaining their ordering
    headers_ordered = []
    headers_set = set()
    for row in rows:
        new_headers = set(row.keys()) - headers_set
        headers_set |= new_headers
        for header in row.keys():
            if header in new_headers:
                headers_ordered.append(header)
    csvwriter.writerow(headers_ordered)
    for row in rows:
        items = []
        for header in headers_ordered:
            item = row.get(header, 'no record')
            if isinstance(item, datetime.datetime):
                item = item.strftime('%Y-%m-%d %H:%M')
            elif isinstance(item, (int, long, float, list, tuple)):
                item = unicode(item)
            elif item is None:
                item = ''
            else:
                item = item.encode('utf8')
            items.append(item)
        try:
            csvwriter.writerow(items)
        except Exception, e:
            raise Exception("%s: %s, %s" % (e, row, items))
    csvout.seek(0)
    return csvout.read()


def ensure_data_is_dicts(data):
    '''Ensure that the data is a list of dicts, rather than a list of tuples
    with column names, as sometimes is the case. Changes it in place'''
    if data['table'] and isinstance(data['table'][0], (list, tuple)):
        new_data = []
        columns = data['columns']
        for row in data['table']:
            new_data.append(OrderedDict(zip(columns, row)))
        data['table'] = new_data
        del data['columns']


def anonymise_user_names(data, organization=None):
    '''Ensure any columns with names in are anonymised, unless the current user
    has privileges.

    NB this is only enabled for data.gov.uk - it is custom functionality.
    '''
    try:
        import ckanext.dgu.lib.helpers as dguhelpers
    except ImportError:
        # If this is not DGU then cannot do the anonymization
        return
    column_names = data['table'][0].keys() if data['table'] else []
    for col in column_names:
        if col.lower() in ('user', 'username', 'user name', 'author'):
            for row in data['table']:
                row[col] = dguhelpers.user_link_info(
                    row[col], organisation=organization)[0]
