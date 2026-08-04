from users.models import Profile, Statistic, User
from django.utils import timezone


# def get_or_save_statistic(request):
#     if request.user.is_authenticated:
#         if not request.profile.visits.filter(day__day__gt=timezone.now().day):
#             Statistic.objects.create(
#                 profile=request.profile
#             )
#         sts = request.profile.visits.filter(day__day__gt=timezone.now().day).first()
#         sts.number += 1
#         sts.save()





