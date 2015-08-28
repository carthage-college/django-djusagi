# -*- coding: utf-8 -*-
import os, sys, json

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_1.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djusagi.settings")

from django.conf import settings

from googleapiclient.discovery import build
#from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

import argparse
import httplib2

"""
Shell script...
"""

# set up command-line options
desc = """
Accepts as input an email address of a google domain super user
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "-e", "--email",
    required=True,
    help="email address of user",
    dest="email"
)
parser.add_argument(
    "--test",
    action='store_true',
    help="Dry run?",
    dest="test"
)

def main():
    """
    main function
    """

    cid = "carthage.edu_gevk047lt1p3llsmmp2fe8rono@group.calendar.google.com"
    with open(settings.SERVICE_ACCOUNT_JSON) as json_file:

        json_data = json.load(json_file)
        #print json_data
        credentials = SignedJwtAssertionCredentials(
            json_data['client_email'],
            json_data['private_key'],
            scope='https://www.googleapis.com/auth/calendar',
            private_key_password='notasecret',
            sub=email
        )

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build("calendar", "v3", http=http)

    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['id'] == cid:
                print calendar_list_entry['summary']
                print calendar_list_entry['description']
                print calendar_list_entry['accessRole']

        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break


######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    email = args.email
    test = args.test

    print args

    sys.exit(main())

