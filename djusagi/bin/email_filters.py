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

from djusagi.core.utils import get_cred

from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.discovery import build

import argparse
import httplib2

import feedparser
import untangle
import gdata.gauth
import gdata.apps.emailsettings.client

"""
Test the google api email settings, with the end goal of displaying
'forwarding' information for any given account
"""

# set up command-line options
desc = """
Accepts as input an email address of a google domain super user
and an optional username.
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "-e", "--email",
    required=True,
    help="email address of administrative user",
    dest="email"
)
parser.add_argument(
    "--username",
    required=False,
    help="username of the account to search",
    dest="username"
)
parser.add_argument(
    "--test",
    action='store_true',
    help="Dry run?",
    dest="test"
)

def get_auth():

    # build our emailsettings credentials
    with open(settings.SERVICE_ACCOUNT_JSON) as json_file:

        json_data = json.load(json_file)
        if test:
            print json_data
        credentials = SignedJwtAssertionCredentials(
            json_data['client_email'],
            json_data['private_key'],
            scope='https://apps-apis.google.com/a/feeds/emailsettings/2.0/',
            sub=email
        )

    credentials.get_access_token()

    if test:
        print credentials.access_token

    # 0Auth2 Token authentication
    auth = gdata.gauth.OAuth2Token(
        credentials.client_id,#serviceEmail
        credentials.client_secret,#private key
        scope='https://apps-apis.google.com/a/feeds/emailsettings/2.0/',
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        user_agent=credentials.user_agent
    )

    return auth

def main():
    """
    main function
    """

    global username
    global email

    auth = get_auth()
    # create our email settings client
    client = gdata.apps.emailsettings.client.EmailSettingsClient(
        domain=email.split('@')[1]
    )
    auth.authorize(client)

    if username:
        forwarding = client.RetrieveForwarding(username=username)
        #print forwarding
        #print forwarding.__dict__
        print forwarding.property[1].value
    else:
        # fetch our users
        service = build(
            "admin", "directory_v1",
            http=get_cred(email, "admin.directory.user")
        )

        user_list = []
        page_token = None
        while True:
            results = service.users().list(
                domain=email.split('@')[1],
                maxResults=500,
                pageToken=page_token,
                orderBy='familyName', viewType='domain_public'
            ).execute()

            page_token = results.get('nextPageToken')
            user_list.append(results)
            if not page_token:
                break

        print "length of user_list: {}".format(len(user_list))

        for users in user_list:

            for user in users["users"]:
                email = user["primaryEmail"]
                username = email.split('@')[0]
                given_name = user['name']['givenName']
                family_name = user['name']['familyName']
                try:
                    forwarding = client.RetrieveForwarding(username=username)
                    if forwarding.property[1].value:
                        print "{}|{}|{}|{}".format(
                            family_name, given_name, email,
                            forwarding.property[1].value
                        )
                except Exception, e:
                    print "{}|{}|{}|{}".format(
                        family_name, given_name, email,
                        str(e)
                    )

######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    email = args.email
    username = args.username
    test = args.test

    if test:
        print args

    sys.exit(main())

