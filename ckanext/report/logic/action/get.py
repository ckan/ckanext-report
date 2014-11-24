from ckanext.report.report_registry import ReportRegistry

import ckan.logic as logic

@logic.side_effect_free
def report_list(context=None, data_dict=None):
    """
    Lists all available reports

    :returns: A list of report dictionaries (see report_show)
    :rtype: list
    """
    logic.check_access('report_list', context, data_dict)
        
    registry = ReportRegistry.instance()
    reports = registry.get_reports()
    return [report.as_dict() for report in reports]

@logic.side_effect_free
def report_show(context=None, data_dict=None):
    """
    Shows a single report

    Does not provide the data for the report which must be obtained by a
    separate call to report_data_get.

    :param report_name: The name of the report
    :type report_name: string

    :returns: A dictionary of information about the report
    :rtype: dictionary
    """
    logic.check_access('report_show', context, data_dict)

    report_name = data_dict.get('report_name')

    report = ReportRegistry.instance().get_report(report_name)

    return report.as_dict()

@logic.side_effect_free
def report_data_get(context=None, data_dict=None):
    """
    Returns the data for the report

    The data may have been cached in the database or may have been generated on
    demand so the date when the data was generated is also returned

    :param report_name: The name of the report
    :type report_name: string

    :param options: Dictionary of options to pass to the report (optional)
    :type options: dict

    :returns: A list containing the data and the date on which it was created
    :rtype: list
    """
    logic.check_access('report_data_get', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options', {})

    report = ReportRegistry.instance().get_report(report_name)

    data, date = report.get_fresh_report(**options)

    return data, date.isoformat()

@logic.side_effect_free
def report_key_get(context=None, data_dict=None):
    """
    Returns a key that will identify the report and options

    :param report_name: The name of the report
    :type report_name: string

    :param options: Dictionary of options to pass to the report
    :type options: dict

    :returns: A key to identify the report 
    :rtype: string
    """
    logic.check_access('report_key_get', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options')

    report = ReportRegistry.instance().get_report(report_name)

    return report.generate_key(options).replace('?', '_')
