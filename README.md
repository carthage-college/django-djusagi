# django-djusagi
Dashboard manager for Google APIs

_Comma separated list of scopes for the service account_

http://www.google.com/m8/feeds,
https://apps-apis.google.com/a/feeds/emailsettings/2.0/,
https://mail.google.com/,
https://spreadsheets.google.com/feeds,
https://www.googleapis.com/auth/admin.directory.group,
https://www.googleapis.com/auth/admin.directory.group.member,
https://www.googleapis.com/auth/admin.directory.orgunit,
https://www.googleapis.com/auth/admin.directory.user,
https://www.googleapis.com/auth/admin.directory.user.alias,
https://www.googleapis.com/auth/admin.directory.user.readonly,
https://www.googleapis.com/auth/admin.directory.user.security,
https://www.googleapis.com/auth/admin.reports.audit.readonly,
https://www.googleapis.com/auth/admin.reports.usage.readonly,
https://www.googleapis.com/auth/apps.groups.settings,
https://www.googleapis.com/auth/calendar,
https://www.googleapis.com/auth/gmail.modify,
https://www.googleapis.com/auth/gmail.readonly,
https://www.googleapis.com/auth/gmail.settings.basic,
https://www.googleapis.com/auth/gmail.settings.sharing,
https://www.googleapis.com/auth/contacts.readonly

_admin console_

https://admin.google.com/

to manage API access, click on the "Security" icon, which takes you to:

https://admin.google.com/AdminHome#SecuritySettings:

click on the "show more" link, then click on "Advanced settings".
you will see one option for Authentication, which has a link to
"Manage API client access".

https://admin.google.com/AdminHome?chromeless=1#OGX:ManageOauthClients


copy the client name and paste it into the "client name" field. copy the
comma separated list above, add any new URLs, remove line breaks,
and paste into the 'One or More API Scopes' field. hit 'authorize'.

_API Manager_
https://console.developers.google.com/apis/dashboard?project=groups-settings&duration=PT1H

Create and manage service accounts, enable and disable Google APIs, etc.

_Migrations_
https://github.com/jhowe-sgs/mailman-to-google-groups
https://developers.google.com/admin-sdk/groups-migration/v1/guides/manage-email-migrations#group_migration_media_upload

_crontab_
# google groups sync
20 02 * * * DJANGO_SETTINGS_MODULE=djusagi.settings.shell ; export DJANGO_SETTINGS_MODULE; (cd /data2/python_venv/3.8/djusagi/ && . bin/activate && bin/python /data2/python_venv/3.8/djusagi/djusagi/bin/groups.py --group=students@carthage.edu --test 2>&1 | mail -s "[DJ Usagi] faculty-staff mailing list group sync" larry@carthage.edu) >> /dev/null 2>&1
20 04 * * * DJANGO_SETTINGS_MODULE=djusagi.settings.shell ; export DJANGO_SETTINGS_MODULE; (cd /data2/python_venv/3.8/djusagi/ && . bin/activate && bin/python /data2/python_venv/3.8/djusagi/djusagi/bin/groups.py --group=faculty-staff@carthage.edu --test 2>&1 | mail -s "[DJ Usagi] faculty-staff mailing list group sync" larry@carthage.edu) >> /dev/null 2>&1
_old crontab_
# google api user reports caching
00 01 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/two_factor_auth.py --who=faculty 2>&1 | mail -s "[djusagi] 2 factor auth caching" larry@carthage.edu) >> /dev/null 2>&1
00 02 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/two_factor_auth.py --who=staff 2>&1 | mail -s "[djusagi] 2 factor auth caching" larry@carthage.edu) >> /dev/null 2>&1
00 03 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/two_factor_auth.py --who=students 2>&1 | mail -s "[djusagi] 2 factor auth caching" larry@carthage.edu) >> /dev/null 2>&1
# google api groups caching
00 04 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/dir_groups_list.py > djusagi/groups.csv) >> /dev/null 2>&1
# groups sync for facstaff and students
00 01 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/groups.py --group=students@carthage.edu  --test | mail -s "[djusagi] groups sync: students" larry@carthage.edu) >> /dev/null 2>&1
00 02 * * * (cd /data2/python_venv/2.7/djusagi/ && . bin/activate && bin/python djusagi/bin/groups.py --group=facstaff@carthage.edu  --test | mail -s "[djusagi] groups sync: students" larry@carthage.edu) >> /dev/null 2>&1
