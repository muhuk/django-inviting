from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_performance_func(settings):
    performance_func = getattr(settings, 'INVITATION_PERFORMANCE_FUNC', None)
    if isinstance(performance_func, (str, unicode)):
        module_name, func_name = performance_func.rsplit('.', 1)
        try:
            performance_func = getattr(import_module(module_name), func_name)
        except ImportError:
            raise ImproperlyConfigured('Can\'t import performance function ' \
                                       '`%s` from `%s`' % (func_name,
                                                           module_name))
    if performance_func and not callable(performance_func):
        raise ImproperlyConfigured('INVITATION_PERFORMANCE_FUNC must be a ' \
                                   'callable or an import path string ' \
                                   'pointing to a callable.')


INVITE_ONLY = getattr(settings, 'INVITATION_INVITE_ONLY', False)
EXPIRE_DAYS = getattr(settings, 'INVITATION_EXPIRE_DAYS', 15)
INITIAL_INVITATIONS = getattr(settings, 'INVITATION_INITIAL_INVITATIONS', 10)
REWARD_THRESHOLD = getattr(settings, 'INVITATION_REWARD_THRESHOLD', 0.75)
PERFORMANCE_FUNC = get_performance_func(settings)
