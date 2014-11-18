from ckan.logic import auth_allow_anonymous_access

@auth_allow_anonymous_access
def report_refresh(context=None, data_dict=None):
    return {'success': False} # Don't allow non-sysadmins
