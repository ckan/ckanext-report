from ckanext.report.report_registry import ReportRegistry

import ckan.logic as logic

def report_refresh(context=None, data_dict=None):
    """
    Causes the cached data of the report to be refreshed

    :param report_name: The name of the report
    :type report_name: string

    :param options: Dictionary of options to pass to the report
    :type options: dict
    """
    logic.check_access('report_refresh', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options')

    report = ReportRegistry.instance().get_report(report_name)

    report.refresh_cache(options)
