import sys

import ckan.plugins as p


class ReportCommand(p.toolkit.CkanCommand):
    """
    Control reports, their generation and caching.

    Reports can be cached if they implement IReportCache. Suitable for ones
    that take a while to run.

    The available commands are:

        initdb - Initialize the database tables for this extension

        list - Lists the reports

        generate - Generate and cache reports - all of them unless you specify
                   a comma separated list of them.

    e.g.

      List all reports:
      $ paster report-cache list -c development.ini

      Generate two reports:
      $ paster report-cache generate openness-scores,broken-links -c development.ini

      Generate all reports:
      $ paster report-cache generate -c development.ini

    """

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2
    min_args = None

    def __init__(self, name):
        super(ReportCommand, self).__init__(name)

    def command(self):
        import logging

        self._load_config()
        self.log = logging.getLogger("ckan.lib.cli")

        if not self.args:
            self.log.error("No arguments supplied and they are required")
            sys.stderr.write(self.usage)
            return
        else:
            cmd = self.args[0]
            if cmd == 'initdb':
                self._initdb()
            elif cmd == 'list':
                self._list()
            elif cmd == 'generate':
                report_list = None
                if len(self.args) == 2:
                    report_list = [s.strip() for s in self.args[1].split(',')]
                    self.log.info("Running reports => %s", report_list)
                self._generate(report_list)

    def _initdb(self):
        #import ckan.model as model
        #model.Session.remove()
        #model.Session.configure(bind=model.meta.engine)
        #log.info("Database access initialised")

        from ckanext.report import model as report_model
        report_model.init_tables()
        self.log.info('Report table is setup')


    def _list(self):
        from ckanext.report.report_registry import ReportRegistry
        registry = ReportRegistry.instance()
        for plugin, report_name, report_title in registry.get_names():
            report = registry.get_report(report_name)
            date = report.get_cached_date()
            print '%s: %s %s' % (plugin, report_name,
                  date.strftime('%d/%m/%Y %H:%M') if date else '(not cached)')

    def _generate(self, report_list=None):
        from ckanext.report.report_registry import ReportRegistry
        registry = ReportRegistry.instance()
        if report_list:
            for report_name in report_list:
                registry.get_report(report_name).refresh_cache_for_all_options()
        else:
            registry.refresh_cache_for_all_reports()
