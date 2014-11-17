from ckanext.report.report_registry import ReportRegistry

def report_list(context=None, data_dict=None):
    registry = ReportRegistry.instance()
    reports = registry.get_reports()
    return [{'name': report.name, 
             'title': report.title, 
             'description': report.description} for report in reports]
