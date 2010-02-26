from django import template
from invitation.app_settings import INVITE_ONLY


register = template.Library()


@register.inclusion_tag('admin/invitation/invitationstats/_reward_link.html')
def admin_reward_link():
    """
    Adds a reward action if INVITE_ONLY is ``True``.

    Usage::

        {% admin_reward_link %}
    """
    return {'INVITE_ONLY': INVITE_ONLY}
