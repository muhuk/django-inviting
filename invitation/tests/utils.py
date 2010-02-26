import os
from django.core.urlresolvers import clear_url_caches
from django.utils.importlib import import_module
from django.contrib.auth.models import User
from test_settings import SettingsTestCase


class BaseTestCase(SettingsTestCase):
    urls = 'invitation.tests.urls'

    def setUp(self):
        super(BaseTestCase, self).setUp()
        TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__),
                                      'templates'),)
        self.settings_manager.set(TEMPLATE_DIRS=TEMPLATE_DIRS)
        User.objects.create_user('testuser',
                                 'testuser@example.com',
                                 'testuser')

    def user(self):
        return User.objects.get(username='testuser')

    def reset_urlconf(self):
        reload(import_module('invitation.urls'))
        reload(import_module('invitation.tests.urls'))
        clear_url_caches()
