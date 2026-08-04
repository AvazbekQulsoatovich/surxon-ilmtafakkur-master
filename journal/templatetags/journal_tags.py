from django import template
from django.db.models import Count, Sum
from journal.models import SocialMedia, Contact
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import Statistic

User = get_user_model()

register = template.Library()


@register.simple_tag
def get_social_media():
    return SocialMedia.objects.all()


@register.simple_tag
def get_messages_count():
    count = Contact.objects.filter(is_read=False).aggregate(
        count=Count('pk')
    )['count']
    return count


@register.simple_tag
def get_users_count():
    return User.objects.count()


@register.filter
def minus(total, number):
    result: int = int(total) - int(number)
    return abs(result)
