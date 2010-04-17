from django.utils.importlib import import_module
from invitation import app_settings


app_settings.INVITE_ONLY = False
reload(import_module('invitation.urls'))
reload(import_module('invitation.tests.urls'))
from invitation.tests.urls import urlpatterns
