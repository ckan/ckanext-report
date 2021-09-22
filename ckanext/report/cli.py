# -*- coding: utf-8 -*-

import click
import ckanext.report.utils as utils


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

    if report_list:
        report_list = [s.strip() for s in report_list.split(',')]
    timings = utils.generate(report_list)

    click.secho(u'Report generation complete %s' % timings, fg=u"green")


@report.command()
def list():
    utils.list()


@report.command()
@click.argument(u'report_name')
@click.argument(u'report_options', nargs=-1)
def generate_for_options(report_name, report_options):
    message = utils.generate_for_options(report_name, report_options)
    if message:
        click.secho(message, fg=u"red")
