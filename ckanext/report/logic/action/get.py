from ckanext.report.report_registry import ReportRegistry

import ckan.logic as logic

@logic.side_effect_free
def report_list(context=None, data_dict=None):
    """
    Lists all available reports
    """
    logic.check_access('report_list', context, data_dict)
        
    registry = ReportRegistry.instance()
    reports = registry.get_reports()
    return [{'name': report.name, 
             'title': report.title, 
             'description': report.description} for report in reports]

@logic.side_effect_free
def report_show(context=None, data_dict=None):
    """
    Shows a single report

    Does not provide the data for the report which must be obtained by a
    separate call to report_data_get.

    The name of the report is required as a parameter in the data_dict
    """
    logic.check_access('report_show', context, data_dict)

    report_name = data_dict.get('report_name')

    report = ReportRegistry.instance().get_report(report_name)

    return {'name': report.name,
            'title': report.title,
            'description': report.description,
            'option_defaults': report.option_defaults,
            'template': report.get_template()}

@logic.side_effect_free
def report_data_get(context=None, data_dict=None):
    """
    Returns the data for the report

    The data may have been cached in the database or may have been generated on
    demand so the date when the data was generated is also returned

    The name of the report is required as a parameter in the data_dict

    Optionally you may provide an 'options' key in the data_dict which should
    be a dictionary of options which are passed to the report
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

    The name of the report is required as a parameter in the data_dict

    A dictionary of options is required as a parameter in the data_dict
    """
    logic.check_access('report_key_get', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options')

    report = ReportRegistry.instance().get_report(report_name)

    return report.generate_key(options).replace('?', '_')
