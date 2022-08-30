# encoding: utf-8

import click

from . import utils


def get_commands():
    return [report]


@click.group()
def report():
    """Generates reports"""
    pass


@report.command()
def initdb():
    """Creates necessary db tables"""
    utils.initdb()
    click.secho(u'Report table is setup', fg=u"green")


@report.command()
@click.argument(u'report_list', required=False)
def generate(report_list):
    """
    Generate and cache reports - all of them unless you specify
    a comma separated list of them.
    """
    if report_list:
        report_list = [s.strip() for s in report_list.split(',')]
    timings = utils.generate(report_list)

    click.secho(u'Report generation complete %s' % timings, fg=u"green")


@report.command()
def list():
    """ Lists the reports
    """
    utils.list_reports()


@report.command()
@click.argument(u'report_name')
@click.argument(u'report_options', nargs=-1)
def generate_for_options(report_name, report_options):
    """
    Generate and cache a report for one combination of option values.
    You can leave it with the defaults or specify options
    as more parameters: key1=value key2=value
    """
    message = utils.generate_for_options(report_name, report_options)
    if message:
        click.secho(message, fg=u"red")
