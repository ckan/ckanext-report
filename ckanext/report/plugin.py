# encoding: utf-8

import ckan.plugins as p
from ckan.plugins import toolkit

from . import helpers as h
from .interfaces import IReport
from .logic.action import get as action_get, update as action_update
from .logic.auth import get as auth_get, update as auth_update

if h.is_ckan_29():
    from .plugin_mixins.flask_plugin import MixinPlugin
else:
    from .plugin_mixins.pylons_plugin import MixinPlugin


class ReportPlugin(MixinPlugin, p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'report__relative_url_for': h.relative_url_for,
            'report__chunks': h.chunks,
            'report__organization_list': h.organization_list,
            'report__render_datetime': h.render_datetime,
            'report__explicit_default_options': h.explicit_default_options,
            'is_ckan_29': h.is_ckan_29,
        }

    # IActions
    def get_actions(self):
        return {'report_list': action_get.report_list,
                'report_show': action_get.report_show,
                'report_data_get': action_get.report_data_get,
                'report_key_get': action_get.report_key_get,
                'report_refresh': action_update.report_refresh}

    # IAuthFunctions
    def get_auth_functions(self):
        return {'report_list': auth_get.report_list,
                'report_show': auth_get.report_show,
                'report_data_get': auth_get.report_data_get,
                'report_key_get': auth_get.report_key_get,
                'report_refresh': auth_update.report_refresh}


class TaglessReportPlugin(p.SingletonPlugin):
    '''
    This is a working example only. To be kept simple and demonstrate features,
    rather than be particularly meaningful.
    '''
    p.implements(IReport)

    # IReport

    def register_reports(self):
        from ckanext.report import reports
        return [reports.tagless_report_info]
