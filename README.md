# ckanext-report

ckanext-report is a CKAN extension that provides a reporting infrastructure. Here are the features offered:

* All available reports are listed on a central web page and from the command-line.
* Breadcrumbs allow navigation from a report back to the reports page.
* Reports are served as a web page, JSON or CSV from a cache.
* The reports can be run in a nightly batch and saved to the cache.
* Admins can regenerate reports from the report's web page.

A number of extensions currently offer reports that rely on this extension, e.g. ckanext-archiver, ckanext-qa, ckanext-dgu.

TODO:

* Stop a report from being generated multiple times in parallel (unnecessary waste) - use a queue?
* Stop more than one report being generated in parallel (high load for the server) - maybe use a queue.


## Install & setup

Install ckanext-report into your CKAN virtual environment in the usual way:

    (pyenv) $ pip install -e git+https://github.com/datagovuk/ckanext-report.git#egg=ckanext-report

Initialize the database tables needed by ckanext-report:

    (pyenv) $ paster --plugin=ckanext-report report initdb --config=mysite.ini

Enable the plugin. In your config (e.g. development.ini or production.ini) add ``report`` to your ckan.plugins. e.g.:

    ckan.plugins = report

Get the list of reports:

    (pyenv) $ paster --plugin=ckanext-report report list --config=mysite.ini

Generate all reports:

    (pyenv) $ paster --plugin=ckanext-report report generate --config=mysite.ini


## Command-line interface

The following operations can be run from the command line using the ``paster --plugin=ckanext-report report`` command:

```
  report list
    - lists the reports

  report generate [report1,report2,...]
    - generate the specified reports, or all of them if none specified
```

e.g.:

    (pyenv) $ paster --plugin=ckanext-report report list --config=mysite.ini


## Dataset Notes

Reports that examine datasets include a column 'Dataset Notes', designed to show custom properties of the datasets. There are often key properties that you want to show, such as whether a dataset is private, harvested etc., but it is configurable because every CKAN install is different. To configure the contents of this: put a python expression in the CKAN config `ckanext-report.notes.dataset`.

For example at data.gov.uk we flag up if a dataset is 'unpublished', has been harvested or was imported from ONSHUB:

```
ckanext-report.notes.dataset = ' '.join(('Unpublished' if asbool(pkg.extras.get('unpublished')) else '', 'UKLP' if asbool(pkg.extras.get('UKLP')) else '', 'National Statistics Pub Hub' if pkg.extras.get('external_reference')=='ONSHUB' else ''))
```

# Creating a Report

A report has three key elements:

1. Report Code - a python function that produces the report. 
2. Template - HTML for displaying the report data.
3. Registration - containing the configuration of the report.

## Report Code

The code that produces the report will probably make some calls to the logic layer or database, assemble the data into dicts/lists and then return them. This will be saved as JSON in the database data_cache.

The returned data should be a dict like this:

```javascript
{'table': [
    {'tag': 'history', 'count': 12, 'user': 'bob', 'created': '2008-06-13T10:24:59.435631'},
    {'tag': 'science', 'count': 4, 'user': 'bob', 'created': '2009-12-14T08:42:45.473827'},
    {'tag': 'geography', 'count': 5, 'user': 'bob', 'created': '2012-01-02T16:34:24.958284'}
    ]
    'total_tags_used': 21,
    'last_added': '2014-04-13T20:40:20.123456'
}
```
  
There should be a `table` with the main body of the data, and any other totals or incidental pieces of data.

  Note: the table is required because of the CSV download facility, and CSV demands a table. (The CSV download only includes the table, ignoring any other values in the data.) Although the data has to essentially be stored as a table, you do have the option to display it differently in the web page by using a clever template.

Dates should be returned as an ISO format string.

The convention is to put the report code in: `ckanext/<extension>/reports.py`

## Template

When you view a report, ckanext-report will automatically show the title, options, the CSV/JSON download buttons and for the administrator a 'refresh' button. Everything below that, the display of the data itself, is the job of the report template.

The report template will probably display the incidental data and then the table:

```html
<ul>
    <li>Number of tag usages: ${c.data['total_tags_used']}</li>
    <li>Longest tag: ${c.data['longest_tag']} letters</li>
    <li>Last tag added: ${h.render_datetime(c.data['last_added'])}</li>
</ul>

<table class="table table-bordered table-condensed tablesorter" id="report-table" style="width: 100%; table-layout:fixed; margin-top: 8px;">
    <thead>
      <tr>
        <th>Tag</th>
        <th>Count</th>
        <th>User</th>
        <th>Created</th>
      </tr>
    </thead>
    <tbody>
      <py:for each="row in c.data['table']">
        <tr>
          <td>
            <a href="${h.url_for(controller='tag', action='view', id=row['tag'])}">
              ${row['tag']}
            </a>
          </td>
          <td>${row['count']}</td>
          <td>${h.linked_user(row['user'])}</td>
          <td>${h.render_datetime(row['created'])}</td>
        </tr>
      </py:for>
    </tbody>
</table>
```

The convention is to put the report templates in: `ckanext/<extension>/templates/report/<report_name>.html`

Note: ckanext-report currently has Genshi templates, due to the author still using legacy templates from pre-CKAN 1.8. Feel free to update them to Jinja, used by CKAN 2+ - there isn't a lot to change.

## Registration

Register your report with ckanext-report with the IReport plugin and supply its configuration.

Your extension will probably have a file `plugin.py` defining plugins - classes which inherit from `p.SingletonPlugin`. Make a plugin implement IReport, based on this example plugin.py:

```python
import ckan.plugins as p
from ckanext.report.interfaces import IReport

class TagPlugin(p.SingletonPlugin):
    p.implements(IReport)

    # IReport

    def register_reports(self):
        import reports
        return [reports.tag_report_info]
```

The last line refers to `tag_report_info` which is a dictionary with properties of the report. This is stored in `reports.py` together with the report code (see above). The info dict looks like this:

```python
from ckan.lib.helpers import OrderedDict
tag_report_info = {
    'name': 'tag-lengths',
    'option_defaults': OrderedDict((('organization', None),
                                    ('include_sub_organizations', False),
                                    )),
    'option_combinations': tag_report_option_combinations,
    'generate': tag_report,
    'template': 'report/tags.html',
    }
```

Required keys:

* name - forms part of the URL
* title (optional) - this is the report title as it is displayed. Defaults to name, capitalized and with dashes changed to spaces.
* description (optional) - this is displayed in the report list page and on the report page.
* generate - function returning the report data
* template - filepath of the report HTML template
* option_defaults - dict of ALL option names and their default values
* option_combinations - function returning a list of all the options combinations (reports for these combinations are generated by default)

Finally we need to define the function that returns the option_combinations:
```
def tag_report_option_combinations():
    for organization in all_organizations(include_none=True):
        for include_sub_organizations in (False, True):
            yield {'organization': organization,
                   'include_sub_organizations': include_sub_organizations}

```
