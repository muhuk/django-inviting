from sys import stdout

from django.contrib.auth.models import User
from django.db.models.signals import post_syncdb
from invitation import models


def create_stats_for_all_users(sender, **kwargs):
    """
    Create `InvitationStats` objects for all users after a `sycndb`

    """
    for u in User.objects.all():
        models.InvitationStats.objects.create(user=u)
    stdout.write("Created InvitationStats for all existing Users\n")

post_syncdb.connect(create_stats_for_all_users, sender=models)
