# encoding: utf-8

import ckan.plugins as p

from . import utils


class ReportCommand(p.toolkit.CkanCommand):
    """
    Control reports, their generation and caching.

    Reports can be cached if they implement IReportCache. Suitable for ones
    that take a while to run.

    The available commands are:

        initdb   - Initialize the database tables for this extension

        list     - Lists the reports

        generate - Generate and cache reports - all of them unless you specify
                   a comma separated list of them.

        generate-for-options - Generate and cache a report for one combination
                   of option values. You can leave it with the defaults or
                   specify options as more parameters: key1=value key2=value

    e.g.

      List all reports:
      $ paster report list

      Generate two reports:
      $ paster report generate openness-scores,broken-links

      Generate report for one specified option value(s):
      $ paster report generate-for-options publisher-activity organization=cabinet-office

      Generate all reports:
      $ paster report generate

    """

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def __init__(self, name):
        super(ReportCommand, self).__init__(name)

    def command(self):
        import logging

        self._load_config()
        self.log = logging.getLogger("ckan.lib.cli")

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
        elif cmd == 'generate-for-options':
            message = utils.generate_for_options(self.args[1], self.self.args[2:])
            if message:
                self.parser.error(message)
        else:
            self.parser.error('Command not recognized: %r' % cmd)

    def _initdb(self):
        utils.initdb()
        self.log.info('Report table is setup')

    def _list(self):
        utils.list()

    def _generate(self, report_list=None):

        timings = utils.generate(report_list)
        self.log.info("Report generation complete %s", timings)
