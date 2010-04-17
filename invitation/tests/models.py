import datetime
from django.core import mail
from django.contrib.auth.models import User
from utils import BaseTestCase
from invitation import app_settings
from invitation.models import InvitationError, Invitation, InvitationStats
from invitation.models import performance_calculator_invite_only
from invitation.models import performance_calculator_invite_optional


EXPIRE_DAYS = app_settings.EXPIRE_DAYS
INITIAL_INVITATIONS = app_settings.INITIAL_INVITATIONS


class InvitationTestCase(BaseTestCase):
    def setUp(self):
        super(InvitationTestCase, self).setUp()
        user = self.user()
        user.invitation_stats.use()
        self.invitation = Invitation.objects.create(user=user,
                                                    email=u'test@example.com',
                                                    key=u'F' * 40)

    def make_invalid(self, invitation=None):
        invitation = invitation or self.invitation
        invitation.date_invited = datetime.datetime.now() - \
                                  datetime.timedelta(EXPIRE_DAYS + 10)
        invitation.save()
        return invitation

    def test_send_email(self):
        self.invitation.send_email()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], u'test@example.com')
        self.invitation.send_email(u'other@email.org')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].recipients()[0], u'other@email.org')

    def test_mark_accepted(self):
        new_user = User.objects.create_user('test', 'test@example.com', 'test')
        pk = self.invitation.pk
        self.invitation.mark_accepted(new_user)
        self.assertRaises(Invitation.DoesNotExist,
                          Invitation.objects.get, pk=pk)

    def test_invite(self):
        self.user().invitation_stats.add_available(10)
        Invitation.objects.all().delete()
        invitation = Invitation.objects.invite(self.user(), 'test@example.com')
        self.assertEqual(invitation.user, self.user())
        self.assertEqual(invitation.email, 'test@example.com')
        self.assertEqual(len(invitation.key), 40)
        self.assertEqual(invitation.is_valid(), True)
        self.assertEqual(type(invitation.expiration_date()), datetime.date)
        # Test if existing valid record is returned
        # when we try with the same credentials
        self.assertEqual(Invitation.objects.invite(self.user(),
                                              'test@example.com'), invitation)
        # Try with an invalid invitation
        invitation = self.make_invalid(invitation)
        new_invitation = Invitation.objects.invite(self.user(),
                                                   'test@example.com')
        self.assertEqual(new_invitation.is_valid(), True)
        self.assertNotEqual(new_invitation, invitation)

    def test_find(self):
        self.assertEqual(Invitation.objects.find(self.invitation.key),
                         self.invitation)
        invitation = self.make_invalid()
        self.assertEqual(invitation.is_valid(), False)
        self.assertRaises(Invitation.DoesNotExist,
                          Invitation.objects.find, invitation.key)
        self.assertEqual(Invitation.objects.all().count(), 0)
        self.assertRaises(Invitation.DoesNotExist,
                          Invitation.objects.find, '')


class InvitationStatsBaseTestCase(BaseTestCase):
    def stats(self, user=None):
        user = user or self.user()
        return (user.invitation_stats.available,
                user.invitation_stats.sent,
                user.invitation_stats.accepted)

    class MockInvitationStats(object):
        def __init__(self, available, sent, accepted):
            self.available = available
            self.sent = sent
            self.accepted = accepted


class InvitationStatsInviteOnlyTestCase(InvitationStatsBaseTestCase):
    def setUp(self):
        super(InvitationStatsInviteOnlyTestCase, self).setUp()
        app_settings.INVITE_ONLY = True

    def test_default_performance_func(self):
        self.assertAlmostEqual(performance_calculator_invite_only(
                                     self.MockInvitationStats(5, 5, 1)), 0.42)
        self.assertAlmostEqual(performance_calculator_invite_only(
                                     self.MockInvitationStats(0, 10, 10)), 1.0)
        self.assertAlmostEqual(performance_calculator_invite_only(
                                     self.MockInvitationStats(10, 0, 0)), 0.0)

    def test_add_available(self):
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS, 0, 0))
        self.user().invitation_stats.add_available()
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 1, 0, 0))
        self.user().invitation_stats.add_available(10)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 11, 0, 0))

    def test_use(self):
        self.user().invitation_stats.add_available(10)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 10, 0, 0))
        self.user().invitation_stats.use()
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 9, 1, 0))
        self.user().invitation_stats.use(5)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 4, 6, 0))
        self.assertRaises(InvitationError,
                          self.user().invitation_stats.use,
                          INITIAL_INVITATIONS + 5)

    def test_mark_accepted(self):
        if INITIAL_INVITATIONS < 10:
            i = 10
            self.user().invitation_stats.add_available(10-INITIAL_INVITATIONS)
        else:
            i = INITIAL_INVITATIONS
        self.user().invitation_stats.use(i)
        self.user().invitation_stats.mark_accepted()
        self.assertEqual(self.stats(), (0, i, 1))
        self.user().invitation_stats.mark_accepted(5)
        self.assertEqual(self.stats(), (0, i, 6))
        self.assertRaises(InvitationError,
                          self.user().invitation_stats.mark_accepted, i)

    def test_give_invitations(self):
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS, 0, 0))
        InvitationStats.objects.give_invitations(count=3)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 3, 0, 0))
        InvitationStats.objects.give_invitations(self.user(), count=3)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 6, 0, 0))
        InvitationStats.objects.give_invitations(self.user(),
                                                 count=lambda u: 4)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS + 10, 0, 0))

    def test_reward(self):
        self.assertAlmostEqual(self.user().invitation_stats.performance, 0.0)
        InvitationStats.objects.reward()
        self.assertEqual(self.user().invitation_stats.available,
                         INITIAL_INVITATIONS)
        self.user().invitation_stats.use(INITIAL_INVITATIONS)
        self.user().invitation_stats.mark_accepted(INITIAL_INVITATIONS)
        InvitationStats.objects.reward()
        invitation_stats = self.user().invitation_stats
        self.assertEqual(invitation_stats.performance > 0.5, True)
        self.assertEqual(invitation_stats.available, INITIAL_INVITATIONS)


class InvitationStatsInviteOptionalTestCase(InvitationStatsBaseTestCase):
    def setUp(self):
        super(InvitationStatsInviteOptionalTestCase, self).setUp()
        app_settings.INVITE_ONLY = False

    def test_default_performance_func(self):
        self.assertAlmostEqual(performance_calculator_invite_optional(
                                     self.MockInvitationStats(5, 5, 1)), 0.2)
        self.assertAlmostEqual(performance_calculator_invite_optional(
                                     self.MockInvitationStats(20, 5, 1)), 0.2)
        self.assertAlmostEqual(performance_calculator_invite_optional(
                                     self.MockInvitationStats(0, 5, 1)), 0.2)
        self.assertAlmostEqual(performance_calculator_invite_optional(
                                     self.MockInvitationStats(0, 10, 10)), 1.0)
        self.assertAlmostEqual(performance_calculator_invite_optional(
                                     self.MockInvitationStats(10, 0, 0)), 0.0)

    def test_use(self):
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS, 0, 0))
        self.user().invitation_stats.use()
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS, 1, 0))
        self.user().invitation_stats.use(5)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS, 6, 0))
        self.user().invitation_stats.use(INITIAL_INVITATIONS + 5)
        self.assertEqual(self.stats(), (INITIAL_INVITATIONS,
                                        INITIAL_INVITATIONS + 11,
                                        0))

    def test_mark_accepted(self):
        if INITIAL_INVITATIONS < 10:
            i = 10
            self.user().invitation_stats.add_available(10-INITIAL_INVITATIONS)
        else:
            i = INITIAL_INVITATIONS
        self.user().invitation_stats.use(i)
        self.user().invitation_stats.mark_accepted()
        self.assertEqual(self.stats(), (i, i, 1))
        self.user().invitation_stats.mark_accepted(5)
        self.assertEqual(self.stats(), (i, i, 6))
        self.assertRaises(InvitationError,
                          self.user().invitation_stats.mark_accepted, i)
        self.user().invitation_stats.mark_accepted(4)
        self.assertEqual(self.stats(), (i, i, 10))

    def test_reward(self):
        self.assertAlmostEqual(self.user().invitation_stats.performance, 0.0)
        InvitationStats.objects.reward()
        self.assertEqual(self.user().invitation_stats.available,
                         INITIAL_INVITATIONS)
        self.user().invitation_stats.use(INITIAL_INVITATIONS)
        self.user().invitation_stats.mark_accepted(INITIAL_INVITATIONS)
        InvitationStats.objects.reward()
        invitation_stats = self.user().invitation_stats
        self.assertEqual(
            invitation_stats.performance > app_settings.REWARD_THRESHOLD, True)
        self.assertEqual(invitation_stats.available, INITIAL_INVITATIONS * 2)
