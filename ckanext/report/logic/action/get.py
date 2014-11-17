from ckanext.report.report_registry import ReportRegistry

import ckan.logic as logic

@logic.side_effect_free
def report_list(context=None, data_dict=None):
    logic.check_access('report_list', context, data_dict)
        
    registry = ReportRegistry.instance()
    reports = registry.get_reports()
    return [{'name': report.name, 
             'title': report.title, 
             'description': report.description} for report in reports]

@logic.side_effect_free
def report_get(context=None, data_dict=None):
    logic.check_access('report_get', context, data_dict)

    report_name = data_dict.get('report_name')

    report = ReportRegistry.instance().get_report(report_name)

    return {'name': report.name,
            'title': report.title,
            'description': report.description,
            'option_defaults': report.option_defaults,
            'template': report.get_template()}

@logic.side_effect_free
def report_data_get(context=None, data_dict=None):
    logic.check_access('report_data_get', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options', {})

    report = ReportRegistry.instance().get_report(report_name)

    data, date = report.get_fresh_report(**options)

    return data, date.isoformat()

@logic.side_effect_free
def report_key_get(context=None, data_dict=None):
    logic.check_access('report_key_get', context, data_dict)

    report_name = data_dict.get('report_name')
    options = data_dict.get('options')

    report = ReportRegistry.instance().get_report(report_name)

    return report.generate_key(options).replace('?', '_')
