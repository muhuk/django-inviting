from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


INVITE_ONLY = getattr(settings, 'INVITATION_INVITE_ONLY', False)
EXPIRE_DAYS = getattr(settings, 'INVITATION_EXPIRE_DAYS', 15)
INITIAL_INVITATIONS = getattr(settings, 'INVITATION_INITIAL_INVITATIONS', 10)
REWARD_THRESHOLD = getattr(settings, 'INVITATION_REWARD_THRESHOLD', 0.75)
PERFORMANCE_FUNC = getattr(settings,
                           'INVITATION_PERFORMANCE_FUNC',
                           None)
if isinstance(PERFORMANCE_FUNC, (str, unicode)):
    module_name, func_name = PERFORMANCE_FUNC.rsplit('.', 1)
    print dir(import_module(module_name))
    PERFORMANCE_FUNC = getattr(import_module(module_name), func_name)
if PERFORMANCE_FUNC and not callable(PERFORMANCE_FUNC):
    raise ImproperlyConfigured('INVITATION_PERFORMANCE_FUNC must be a ' \
                               'callable or an import path string pointing ' \
                               'to a callable.')
