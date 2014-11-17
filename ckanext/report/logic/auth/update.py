def report_refresh(context=None, data_dict=None):
    if not (c.userobj and c.userobj.sysadmin):
        return {'success': False}
    else:
        return {'success': True}
