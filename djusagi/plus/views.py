import os
import logging
import httplib2

from googleapiclient.discovery import build

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from djusagi.core.models import CredentialsModel

from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

CLIENT_SECRETS = os.path.join(
    os.path.dirname(__file__), '..', 'client_secrets.json'
)

FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    redirect_uri=settings.REDIRECT_URI
)


@login_required
def index(request):
    storage = Storage(CredentialsModel, 'user', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(
            settings.SECRET_KEY, request.user
        )
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("plus", "v1", http=http)
        activities = service.activities()
        activitylist = activities.list(
            collection='public', userId='me'
        ).execute()
        logging.info(activitylist)

    return render(
        request, 'plus/index.html', {'activitylist': activitylist,}
    )


@login_required
def auth_return(request):
    val = xsrfutil.validate_token(
        settings.SECRET_KEY, request.REQUEST['state'], request.user
    )
    if not val:
        #return  HttpResponseBadRequest()
        return render(
            request, 'core/debug.html', {
                'req':request.REQUEST,'val':val,'key':settings.SECRET_KEY
            }
        )
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'user', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect(settings.ROOT_URL)
