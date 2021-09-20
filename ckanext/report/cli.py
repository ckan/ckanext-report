# -*- coding: utf-8 -*-

import click
from ckanext.report import model as report_model


def get_commands():
    return [report]


@click.group()
def report():
    """Generates reports"""
    pass


@report.command()
def initdb():
    """Creates necessary db tables"""
    report_model.init_tables()
    click.secho(u'Report table is setup', fg=u"green")
