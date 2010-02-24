from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from app_settings import INVITE_ONLY


login_required_direct_to_template = login_required(direct_to_template)


urlpatterns = patterns('',
    url(r'^invitation/$',
        login_required_direct_to_template,
        {'template': 'invitation/invitation_home.html'},
        name='invitation_home'),
    url(r'^invitation/invite/$',
        'invitation.views.invite',
        name='invitation_invite'),
    url(r'^invitation/invite/complete/$',
        login_required_direct_to_template,
        {'template': 'invitation/invitation_complete.html'},
        name='invitation_complete'),
    url(r'^invitation/invite/unavailable/$',
        login_required_direct_to_template,
        {'template': 'invitation/invitation_unavailable.html'},
        name='invitation_unavailable'),
    url(r'^invitation/accept/complete/$',
        direct_to_template,
        {'template': 'invitation/invitation_registered.html'},
        name='invitation_registered'),
    url(r'^invitation/accept/(?P<invitation_key>\w+)/$',
        'invitation.views.register',
        name='invitation_register'),
)


if INVITE_ONLY:
    urlpatterns += patterns('',
        url(r'^register/$',
            'django.views.generic.simple.redirect_to',
            {'url': '../invitation/invite_only/', 'permanent': False},
            name='registration_register'),
        url(r'^invitation/invite_only/$',
            direct_to_template,
            {'template': 'invitation/invite_only.html'},
            name='invitation_invite_only'),
        url(r'^invitation/reward/$',
            'invitation.views.reward',
            name='invitation_reward'),
    )
