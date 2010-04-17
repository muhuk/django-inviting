import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        settings.TEMPLATE_DIRS = (
            os.path.join(os.path.dirname(__file__), 'templates'),
        )
        User.objects.create_user('testuser',
                                 'testuser@example.com',
                                 'testuser')

    def user(self):
        return User.objects.get(username='testuser')
