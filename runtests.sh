#! /bin/bash

export PYTHONPATH=${PYTHONPATH}:/opt/google/google_appengine:/opt/google/google_appengine/lib/PyAMF:/opt/google/google_appengine/lib/antlr3:/opt/google/google_appengine/lib/django_1_3:/opt/google/google_appengine/lib/enum:/opt/google/google_appengine/lib/fancy_urllib:/opt/google/google_appengine/lib/google-api-python-client:/opt/google/google_appengine/lib/graphy:/opt/google/google_appengine/lib/grizzled:/opt/google/google_appengine/lib/httplib2:/opt/google/google_appengine/lib/ipaddr:/opt/google/google_appengine/lib/jinja2:/opt/google/google_appengine/lib/markupsafe:/opt/google/google_appengine/lib/oauth2:/opt/google/google_appengine/lib/prettytable:/opt/google/google_appengine/lib/protorpc:/opt/google/google_appengine/lib/python-gflags/tests:/opt/google/google_appengine/lib/simplejson:/opt/google/google_appengine/lib/sqlcmd:/opt/google/google_appengine/lib/webapp2:/opt/google/google_appengine/lib/webob_1_1_1:/opt/google/google_appengine/lib/yaml/lib

python -m unittest discover -s tests