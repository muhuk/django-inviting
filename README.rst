Built on top of ``django-registration``, **django-inviting** handles registration through invitations.


Features
========

- Invitations can be optional or required to be registered.
- Admin integration
- Adding available invitations with custom performance and rewarding
  algorithms. (for invite only mode)


Installation
============

This application depends on ``django-registration``.

#. Add ``"django-inviting"`` directory to your Python path.
#. Add ``"invitation"`` to your ``INSTALLED_APPS`` tuple found in
   your settings file.
#. Include ``"invitation.urls"`` to your URLconf.


Testing & Example
=================

TODO


Usage
=====

You can configure ``django-inviting`` app's behaviour with the following
settings:

:INVITATION_INVITE_ONLY:
    Set this to True if you want registration to be only possible via
    invitations. Default value is ``False``.

:INVITATION_EXPIRE_DAYS:
    How many days before an invitation is expired. Default value is ``15``.

:INVITATION_INITIAL_INVITATIONS:
    How many invitations are available to new users. If
    ``INVITATION_INVITE_ONLY`` is ``False`` this setting
    has no effect. Default value is ``10``.

:INVITATION_PERFORMANCE_FUNC:
    A method that takes an ``InvitationStats`` instance and returns a
    ``float`` between ``0.0`` and ``1.0``. You can supply a custom
    performance method by reference or by import path as a string.
    Default value is ``None``. If a custom performance function is not
    supplied one of the default performance functions in ``invitation.models``
    will be used according to ``INVITATION_INVITE_ONLY`` value.

:INVITATION_REWARD_THRESHOLD:
    A ``float`` that determines which users are rewarded. Default value
    is ``0.75``.


See Also
========

-  `django-invitation <http://code.welldev.org/django-invitation/>`_
-  `django-invite <http://bitbucket.org/lorien/django-invite/>`_

