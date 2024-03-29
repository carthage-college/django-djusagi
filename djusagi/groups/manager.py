# -*- coding: utf-8 -*-

import httplib2

from django.conf import settings
from django.core.cache import cache
from djusagi.core.utils import get_cred
from djusagi.adminsdk.manager.admin import AdminManager
from oauth2client.file import Storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GroupManager:
    """
    Google groups manager.
    see: https://developers.google.com/admin-sdk/directory/reference/rest/v1/members
    """

    def __init__(self):
        """Set up scope and auth credentials."""
        # scope
        scopes = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.user.security',
            'https://www.googleapis.com/auth/apps.groups.settings',
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.directory.group.member',
            'https://apps-apis.google.com/a/feeds/domain/',
            'https://apps-apis.google.com/a/feeds/groups/',
        ]
        # obtain the admin directory user cred
        self.cred = get_cred(scopes)
        #self.cred_admin = get_cred(scopes, account=settings.STORAGE_FILE)

    def service(self):
        """Establish the sevice connection."""
        scopes = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.user.security',
            'https://www.googleapis.com/auth/apps.groups.settings',
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.directory.group.member',
            'https://apps-apis.google.com/a/feeds/domain/',
            'https://apps-apis.google.com/a/feeds/groups/',
        ]
        while True:
            try:
                service = build(
                    'groupsettings',
                    #'directory_v1',
                    'v1',
                    #credentials=self.cred(),
                    credentials=self.cred,
                    #credentials=self.cred_admin,
                )
            except Exception as error:
                print('error = {0}'.format(error))
            else:
                break

        return service

    def groups_get(self, email):
        am = AdminManager()
        service = am.service()
        group = service.groups().get(
            groupKey=email,
            alt='json',
        ).execute()
        return group

    def groups_list(self):
        """Returns all groups in the domain using the adminsdk api."""
        key = "admin_sdk_groups_list"
        groups = cache.get(key)
        if not groups:
            groups = []
            page_token = None
            # build our group list
            am = AdminManager()
            service = am.service()
            while True:
                results = service.groups().list(
                    domain=settings.DOMAIN_USER_EMAIL.split('@')[1],
                    maxResults=500,
                    pageToken=page_token
                ).execute()

                page_token = results.get('nextPageToken')

                for group in results["groups"]:
                    groups.append(group)
                if not page_token:
                    break
            # set cache to expire after 24 hours
            cache.set(key, groups, 86400)
        return groups

    def group_settings(self, email):
        """Retrieves a group's settings from the groups settings api."""
        #key = 'group_settings_{0}'.format(email)
        #gs = cache.get(key)
        gs = False
        if not gs:
            service = self.service()
            gs = service.groups().get(
                groupUniqueId=email,
                alt='json',
            ).execute()
            #while True:
                #try:
                #except Exception as error:
                    #pass
                #else:
                    #break
            #cache.set(key, gs)
        return gs

    def group_owner(self, members):
        """Retrieves the owner of a group from the list of group members."""
        owners = []
        if members:
            for member in members:
                if member['role'] == 'OWNER':
                    owners.append(member)
                    break
        return owners

    def group_members(self, email):
        """Retrieves a group's member list from the admin sdk api."""
        key = 'group_members_{0}'.format(email)
        members = []
        page_token = None
        # build our members list
        am = AdminManager()
        service = am.service()
        while True:
            results = service.members().list(
                groupKey=email,
                alt='json',
                maxResults=200,
                pageToken=page_token,
            ).execute()
            page_token = results.get('nextPageToken')
            if results.get('members'):
                for member in results.get('members'):
                    members.append(member)
            if not page_token:
                break
        return members

    def member_has(self, group, email):
        """Retrieves group member status."""
        am = AdminManager()
        service = am.service()
        return service.members().hasMember(
            groupKey=group,
            memberKey=email,
        ).execute()

    def member_get(self, group, email):
        """Retrieves group member if exists."""
        am = AdminManager()
        service = am.service()
        return service.members().get(
            groupKey=group,
            memberKey=email,
        ).execute()

    def member_insert(self, group, email, member_type):
        """Retrieves group member if exists."""
        am = AdminManager()
        service = am.service()
        body = {
            'email': email,
            'role': 'MEMBER',
            'type': member_type,
            'status': 'ACTIVE',
            'delivery_settings': 'ALL_MAIL',
        }
        response = service.members().insert(
            groupKey=group,
            body=body,
        ).execute()
        return response

    def member_delete(self, group, email):
        """Delete a member from group."""
        am = AdminManager()
        service = am.service()
        response = service.members().delete(
            groupKey=group,
            memberKey=email,
        ).execute()
        return response
