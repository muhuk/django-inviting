from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.models import User
from utils import BaseTestCase
from invitation.models import Invitation


class InviteOnlyModeTestCase(BaseTestCase):
    urls = 'invitation.tests.invite_only_urls'

    def test_invation_mode(self):
        # Normal registration view should redirect
        response = self.client.get(reverse('registration_register'))
        self.assertRedirects(response, reverse('invitation_invite_only'))
        # But registration after invitation view should work
        response = self.client.get(reverse('invitation_register',
                                           args=('A' * 40,)))
        self.assertEqual(response.status_code, 200)

    def test_invitation(self):
        available = self.user().invitation_stats.available
        self.client.login(username='testuser', password='testuser')
        response = self.client.post(reverse('invitation_invite'),
                                    {'email': 'friend@example.com'})
        self.assertRedirects(response, reverse('invitation_complete'))
        self.assertEqual(self.user().invitation_stats.available, available-1)
        # Delete previously created invitation and
        # set available invitations count to 0.
        Invitation.objects.all().delete()
        invitation_stats = self.user().invitation_stats
        invitation_stats.available = 0
        invitation_stats.save()
        del(invitation_stats)
        response = self.client.post(reverse('invitation_invite'),
                                    {'email': 'friend@example.com'})
        self.assertRedirects(response, reverse('invitation_unavailable'))

    def test_registration(self):
        # Make sure error message is shown in
        # case of an invalid invitation key
        response = self.client.get(reverse('invitation_register',
                                           args=('A' * 40,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'invitation/wrong_invitation_key.html')
        # Registration with an invitation
        invitation = Invitation.objects.invite(self.user(),
                                               'friend@example.com')
        register_url = reverse('invitation_register', args=(invitation.key,))
        response = self.client.get(register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'registration/registration_form.html')
        self.assertContains(response, invitation.email)
        # We are posting a different email than the
        # invitation.email but the form should just
        # ignore it and register with invitation.email
        response = self.client.post(register_url,
                                    {'username': u'friend',
                                     'email': u'noone@example.com',
                                     'password1': u'friend',
                                     'password2': u'friend'})
        self.assertRedirects(response, reverse('invitation_registered'))
        self.assertEqual(len(mail.outbox), 0)       # No confirmation email
        self.assertEqual(self.user().invitation_stats.accepted, 1)
        new_user = User.objects.get(username='friend')
        self.assertEqual(new_user.is_active, True)
        self.assertRaises(Invitation.DoesNotExist,
                          Invitation.objects.get,
                          user=self.user(),
                          email='friend@example.com')


class InviteOptionalModeTestCase(BaseTestCase):
    urls = 'invitation.tests.invite_optional_urls'

    def test_invation_mode(self):
        # Normal registration view should work
        response = self.client.get(reverse('registration_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'registration/registration_register.html')
        # So as registration after invitation view
        response = self.client.get(reverse('invitation_register',
                                           args=('A' * 40,)))
        self.assertEqual(response.status_code, 200)

    def test_invitation(self):
        self.client.login(username='testuser', password='testuser')
        response = self.client.get(reverse('invitation_invite'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('invitation_invite'),
                                    {'email': 'friend@example.com'})
        self.assertRedirects(response, reverse('invitation_complete'))
        invitation_query = Invitation.objects.filter(user=self.user(),
                                                   email='friend@example.com')
        self.assertEqual(invitation_query.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.user().invitation_stats.sent, 1)
