from django.contrib import admin
from models import Invitation, InvitationStats


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'expiration_date')
admin.site.register(Invitation, InvitationAdmin)


class InvitationStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'available', 'sent', 'accepted', 'performance')

    def performance(self, obj):
        return '%0.2f' % obj.performance
admin.site.register(InvitationStats, InvitationStatsAdmin)
