from ckanext.report.report_registry import ReportRegistry
from ckan.logic import auth_allow_anonymous_access

@auth_allow_anonymous_access
def report_list(context=None, data_dict=None):
    return {'success': True}

@auth_allow_anonymous_access
def report_get(context=None, data_dict=None):
    return {'success': True}

@auth_allow_anonymous_access
def report_data_get(context=None, data_dict=None):
    report_name = data_dict.get('report_name')

    report = ReportRegistry.instance().get_report(report_name)

    if hasattr(report, 'authorize'):
        user = context['auth_user_obj']
        options =  data_dict['options']
        if not report.authorize(user, options):
            return {'success': False}

    return {'success': True}

@auth_allow_anonymous_access
def report_key_get(context=None, data_dict=None):
    return {'success': True}
