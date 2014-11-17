from ckanext.report.report_registry import ReportRegistry

import ckan.logic as logic

def report_refresh(context=None, data_dict=None):
    logic.check_access('report_refresh', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options')

    report = ReportRegistry.instance().get_report(report_name)

    report.refresh_cache(options)
