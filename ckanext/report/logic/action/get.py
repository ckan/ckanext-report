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
