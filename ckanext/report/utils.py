def initdb():
    from ckanext.report import model as report_model
    report_model.init_tables()


def generate(report_list):
    import time
    from ckanext.report.report_registry import ReportRegistry
    timings = {}

    registry = ReportRegistry.instance()
    if report_list:
        print(report_list)
        for report_name in report_list:
            s = time.time()
            registry.get_report(report_name).refresh_cache_for_all_options()
            timings[report_name] = time.time() - s
    else:
        s = time.time()
        registry.refresh_cache_for_all_reports()
        timings["All Reports"] = time.time() - s

    return timings


def list():
    from ckanext.report.report_registry import ReportRegistry
    registry = ReportRegistry.instance()
    for plugin, report_name, report_title in registry.get_names():
        report = registry.get_report(report_name)
        date = report.get_cached_date()
        print('%s: %s %s' % (plugin, report_name,
                             date.strftime('%d/%m/%Y %H:%M') if date else '(not cached)'))


def generate_for_options(report_name, options):

    report_options = {}

    for option_arg in options:
        if '=' not in option_arg:
            return 'Option needs an "=" sign in it: "%s"' % option_arg
        equal_pos = option_arg.find('=')
        key, value = option_arg[:equal_pos], option_arg[equal_pos+1:]
        if value == '':
            value = None  # this is what the web i/f does with params
        report_options[key] = value

    from ckanext.report.report_registry import ReportRegistry
    registry = ReportRegistry.instance()
    report = registry.get_report(report_name)
    all_options = report.add_defaults_to_options(report_options,
                                                 report.option_defaults)
    report.refresh_cache(all_options)
