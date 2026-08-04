from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.models import BaseModel

User = get_user_model()


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    photo = models.ImageField(upload_to='images/profile/%Y/%m/%d',
                              blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    telephone = models.CharField(max_length=13, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f'Profile for User(id={self.user_id})'


class Statistic(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='visits')
    day = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField(default=0)

    objects = models.Manager()
