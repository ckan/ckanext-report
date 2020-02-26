#!/bin/bash
set -e

if [ $CKANVERSION == 'master' ]
then
    export CKAN_MINOR_VERSION=100
else
    export CKAN_MINOR_VERSION=${CKANVERSION##*.}
fi


if (( $CKAN_MINOR_VERSION >= 9 ))
then
    pytest --ckan-ini=subdir/test.ini --cov=ckanext.report ckanext/report/tests
else
    nosetests --ckan --nologcapture --with-pylons=subdir/test-nose.ini --with-coverage --cover-package=ckanext.report --cover-inclusive --cover-erase --cover-tests ckanext/report/tests/nose
fi