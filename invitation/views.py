from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site, RequestSite
from models import InvitationError, Invitation, InvitationStats
from forms import InvitationForm, RegistrationFormInvitation


@login_required
def invite(request, success_url=None,
           form_class=InvitationForm,
           template_name='invitation/invitation_form.html',):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                invitation = Invitation.objects.invite(
                                     request.user, form.cleaned_data["email"])
            except InvitationError:
                return HttpResponseRedirect(reverse('invitation_unavailable'))
            if Site._meta.installed:
                current_site = Site.objects.get_current()
            else:
                current_site = RequestSite(request)
            invitation.send_email(site=current_site)
            return HttpResponseRedirect(success_url or \
                                               reverse('invitation_complete'))
    else:
        form = form_class()
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))


def register(request,
             invitation_key,
             wrong_key_template='invitation/wrong_invitation_key.html',
             redirect_to_if_authenticated='/',
             success_url=None,
             form_class=RegistrationFormInvitation,
             profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(redirect_to_if_authenticated)
    try:
        invitation = Invitation.objects.find(invitation_key)
    except Invitation.DoesNotExist:
        return render_to_response(wrong_key_template,
                                  {'invitation_key': invitation_key},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = form_class(invitation.email, request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            invitation.mark_accepted(new_user)
            return HttpResponseRedirect(success_url or \
                                             reverse('invitation_registered'))
    else:
        form = form_class(invitation.email)
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)


@staff_member_required
def reward(request):
    rewarded_users, invitations_given = InvitationStats.objects.reward()
    if rewarded_users:
        message = ugettext(u'%(users)s users are given a total of ' \
                           u'%(invitations)s invitations.') % {
                                            'users': rewarded_users,
                                            'invitations': invitations_given}
    else:
        message = ugettext(u'No user has performance above ' \
                           u'threshold, no invitations awarded.')
    request.user.message_set.create(message=message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
