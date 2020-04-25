#!/bin/bash
set -e

echo "This is travis-build.bash..."
echo "Targetting CKAN $CKANVERSION on Python $TRAVIS_PYTHON_VERSION"
if [ $CKANVERSION == 'master' ]
then
    export CKAN_MINOR_VERSION=100
else
    export CKAN_MINOR_VERSION=${CKANVERSION##*.}
fi

export PYTHON_MAJOR_VERSION=${TRAVIS_PYTHON_VERSION%.*}


echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION == 'master' ]
then
    echo "CKAN version: master"
else
    CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
    git checkout $CKAN_TAG
    echo "CKAN version: ${CKAN_TAG#ckan-}"
fi


# install the recommended version of setuptools
if [ -f requirement-setuptools.txt ]
then
    echo "Updating setuptools..."
    pip install -r requirement-setuptools.txt
fi

python setup.py develop

if [ $CKANVERSION == '2.7' ]
then
    echo "Installing setuptools"
    pip install setuptools==39.0.1
fi

if (( $CKAN_MINOR_VERSION >= 9 )) && (( $PYTHON_MAJOR_VERSION == 2 ))
then
    pip install -r requirements-py2.txt
else
    if (( $CKAN_MINOR_VERSION <= 7 ))
    then
        sed -i -r 's/psycopg2==.*//g' requirements.txt
    fi
    pip install -r requirements.txt
fi

# Override psycopg version to avoid problems with Travis and Postgres 10
if (( $CKAN_MINOR_VERSION <= 7 ))
then
    pip install --upgrade psycopg2==2.7.7
fi

pip install -r dev-requirements.txt
cd -

echo "Setting up Solr..."
# solr is multicore for tests on ckan master now, but it's easier to run tests
# on Travis single-core still.
# see https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini

# Fix solr-jetty starting issues https://stackoverflow.com/a/56007895
sudo mkdir /etc/systemd/system/jetty9.service.d
printf "[Service]\nReadWritePaths=/var/lib/solr" | sudo tee /etc/systemd/system/jetty9.service.d/solr.conf
sed '16,21d' /etc/solr/solr-jetty.xml | sudo tee /etc/solr/solr-jetty.xml
sudo systemctl daemon-reload

printf "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_ARGS=\"jetty.http.port=8983\"\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty9
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty9 restart

# Wait for jetty9 to start
timeout 20 bash -c 'while [[ "$(curl -s -o /dev/null -I -w %{http_code} http://localhost:8983)" != "200" ]]; do sleep 2;done'

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan


if (( $CKAN_MINOR_VERSION >= 9 ))
then
    ckan -c test-core.ini db init
else
    paster db init -c test-core.ini
fi
cd -

echo "Installing ckanext-report and its requirements..."
pip install -r requirements.txt
pip install -r dev-requirements.txt
python setup.py develop


echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir
mv test-nose.ini subdir

if (( $CKAN_MINOR_VERSION >= 9 ))
then
    ckan -c subdir/test.ini report initdb
else
    paster report initdb -c subdir/test.ini
fi


echo "travis-build.bash is done."
