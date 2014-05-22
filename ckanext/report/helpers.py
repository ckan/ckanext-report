import ckan.plugins as p


def relative_url_for(**kwargs):
    '''Returns the existing URL but amended for the given url_for-style
    parameters. Much easier than calling h.add_url_param etc.
    '''
    args = dict(p.toolkit.request.environ['pylons.routes_dict'].items()
                + p.toolkit.request.params.items()
                + kwargs.items())
    # remove blanks
    for k, v in args.items():
        if not v:
            del args[k]
    return p.toolkit.url_for(**args)

def chunks(list_, size):
    '''Splits up a given list into 'size' sized chunks.'''
    for i in xrange(0, len(list_), size):
        yield list_[i:i+size]
