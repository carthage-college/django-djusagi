# -*- coding: utf-8 -*-
import os, sys, json

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_1.8/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djusagi.settings")

from django.conf import settings

from djusagi.core.utils import get_cred

from googleapiclient.discovery import build

import argparse
import httplib2

"""
Fetch all users from the Google API for a given domain
and check for aliases
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

    credentials = get_cred(email, "admin.directory.user")
    http = httplib2.Http()

    service = build(
        "admin", "directory_v1", http=credentials.authorize(http)
    )

    user_list = []
    page_token = None
    while True:
        results = service.users().list(
            domain=email.split('@')[1],
            maxResults=100,
            pageToken=page_token,
            orderBy='email', viewType='domain_public'
        ).execute()

        for r in results["users"]:
            user_list.append(r)

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    service = build(
        "gmail", "v1", http=credentials.authorize(http)
    )

    #print "length of user_list: {}".format(len(user_list))
    for user in user_list:
        pmail = user.get('primaryEmail')
        if pmail:
            aliases = service.users().settings().sendAs().list(userId=pmail).execute()
            for alias in aliases.get('sendAs'):
                print '{}|{}|{}'.format(
                    user.get('name').get('fullName'),
                    user.get('primaryEmail'), alias.get('sendAsEmail')
                )



######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    email = args.email
    test = args.test

    print args

    sys.exit(main())
