from django.contrib import admin

from .models import Profile, Statistic


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', 'date_birth', 'is_admin')
    list_display_links = ('id', 'user')
    list_editable = ('is_admin',)


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('profile', 'day', 'number',)

