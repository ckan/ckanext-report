# encoding: utf-8

import datetime
import logging
import json

from sqlalchemy import types, Table, Column, Index, MetaData
from sqlalchemy.orm import mapper

from ckan import model
import ckan.plugins as p
from ckan.plugins.toolkit import config
try:
    from collections import OrderedDict  # from python 2.7
except ImportError:
    from sqlalchemy.util import OrderedDict

log = logging.getLogger(__name__)

__all__ = ['DataCache', 'data_cache_table', 'init_tables']

metadata = MetaData()

data_cache_table = Table(
    'data_cache', metadata,
    Column('id', types.UnicodeText, primary_key=True,
           default=model.types.make_uuid),
    Column('object_id', types.UnicodeText, index=True),
    Column('key', types.UnicodeText, nullable=False),
    Column('value', types.UnicodeText),
    Column('created', types.DateTime, default=datetime.datetime.utcnow),
)
Index('idx_data_cache_object_id_key', data_cache_table.c.object_id,
      data_cache_table.c.key)


class DataCache(object):
    """
    DataCache provides simple caching of pre-calculated values for queries that
    would take too long to run in real time.  It allows background tasks to
    determine what it wants to store, and then uses this model to store that
    data, so that at request time the data can be fetched in bulk.

    This model makes no assumptions on what is stored, and so it is up to the
    producer and consumer to agree on a format for the value stored.  It is
    suggested that for data that is not a basic type (int, string etc) that
    json is used as decoding of JSON will still be a lot faster than performing
    the initial queries.

    Example usage:

        >>> pub_id = '1234'
        >>> DataCache.set(pub_id, "broken_link_count", 2112)
        >>> DataCache.get(pub_id, "broken_link_count")
        2112

    One might question why not just use Memcached or Redis? These offer
    key-value pair storage too, but lack a couple of things wanted for the
    cached_reports: 1. the creation time is pretty important to know for every
    item. It is easier to store alongside the key & value rather than in the
    value structure. 2. the object_id can be joined to package, resource or
    group when desired. 3. this cache stores things that could take longer to
    generate than the 30s request time-out (or indeed a user's patience). So in
    that sense it is not so much a cache, but a store of application data,
    which happens to be refreshed regularly, so suitable for storage in the
    main application db, rather than any volatile external cache.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def get(cls, object_id, key, convert_json=False, max_age=None):
        """
        Retrieves the value and date that it was written if the record with
        object_id/key exists. If not it will return None/None.
        """
        item = model.Session.query(cls)\
                    .filter(cls.key == key)\
                    .filter(cls.object_id == object_id)\
                    .first()
        if not item:
            return (None, None)

        if max_age is not None:
            age = datetime.datetime.utcnow() - item.created
            if age > max_age:
                log.debug('Cache not returned - it is older than requested %s/%s %r > %r',
                          object_id, key, age, max_age)
                return (None, None)

        value = item.value
        if convert_json:
            # Use OrderedDict instead of dict, so that the order of the columns
            # in the data is preserved from the data when it was written (assuming
            # it was written as an OrderedDict in the report's code).
            try:
                # Python 2.7's json library has object_pairs_hook
                import json
                value = json.loads(value, object_pairs_hook=OrderedDict)
            except TypeError:  # Untested
                # Python 2.4-2.6
                import simplejson as json
                value = json.loads(value, object_pairs_hook=OrderedDict)
        return value, item.created

    @classmethod
    def get_if_fresh(cls, *args, **kwargs):
        # Get cache if it is less than 2 (or as configured) days old.
        max_age_in_days = p.toolkit.asint(config.get(
            'ckanext-report.max_age_in_days', 2
        ))
        max_age = datetime.timedelta(days=max_age_in_days)
        return cls.get(*args, max_age=max_age, **kwargs)

    @classmethod
    def set(cls, object_id, key, value, convert_json=False):
        """
        This method looks up any existing record for the object_id/key and if
        found will update the value and created fields, otherwise it will
        create a new record.  All values will be returned as a string, unless
        convert_json is done to convert from JSON.
        """
        if convert_json:
            value = json.dumps(value)

        item = model.Session.query(cls) \
                    .filter(cls.key == key) \
                    .filter(cls.object_id == object_id).first()
        if item is None:
            item = DataCache(object_id=object_id, key=key, value=value)
            model.Session.add(item)
        else:
            item.value = value
        item.created = datetime.datetime.utcnow()

        log.debug('Cache save: %s/%s', object_id, key)
        model.Session.flush()
        return item.created


mapper(DataCache, data_cache_table)


def init_tables():
    metadata.create_all(model.meta.engine)
