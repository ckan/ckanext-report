import ckan.plugins as p
from ckanext.report.interfaces import IReport

class ReportPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # IRoutes

    def before_map(self, map):
        report_ctlr = 'ckanext.report.controllers:ReportController'
        map.connect('reports', '/report', controller=report_ctlr,
                    action='index')
        map.redirect('/reports', '/report')
        map.connect('report', '/report/:report_name', controller=report_ctlr,
                    action='view')
        map.connect('report-org', '/report/:report_name/:organization',
                    controller=report_ctlr, action='view')
        return map

    # IConfigurer

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')

    # ITemplateHelpers

    def get_helpers(self):
        from ckanext.report import helpers as h
        return {
            'report__relative_url_for': h.relative_url_for,
            'report__chunks': h.chunks,
            }


class TaglessReportPlugin(p.SingletonPlugin):
    '''
    This is a working example only. To be kept simple and demonstrate features,
    rather than be particularly meaningful.
    '''
    p.implements(IReport)

    # IReport

    def register_reports(self):
        import reports
        return [reports.tagless_report_info]

