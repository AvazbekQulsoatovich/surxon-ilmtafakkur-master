from django.contrib.auth import get_user_model
from users.models import Profile, Statistic
from django.utils import timezone

User = get_user_model()


class ProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            if not request.__dict__.get('profile', None):
                request.profile, _ = Profile.objects.get_or_create(user=request.user)

        else:
            request.profile = None

        response = self.get_response(request)
        return response