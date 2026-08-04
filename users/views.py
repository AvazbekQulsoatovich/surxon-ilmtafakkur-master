from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
# from journal.functions import get_or_save_statistic

from .forms import UserCreateForm, ProfileCreateForm, LoginForm, UserUpdateForm


User = get_user_model()


def register(request: HttpRequest):
    # get_or_save_statistic(request)
    if request.method == 'POST':
        user_form = UserCreateForm(data=request.POST)
        profile_form = ProfileCreateForm(data=request.POST,
                                         files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(
                user_form.cleaned_data['password']
            )
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Siz ro'yxatdan mavaffaqiyatli o'tdingiz! ✅")
            return redirect('users:login')
        else:
            messages.warning(request, "Ro'yxatdan o'tmadiz, ya'na harakat qilib ko'ring! ⚠️")
    else:
        user_form = UserCreateForm()
        profile_form = ProfileCreateForm()

    return render(request, 'users/signup.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


def user_login(request: HttpRequest):
#     get_or_save_statistic(request)
    if request.method == 'POST':
        user_form = LoginForm(data=request.POST)
        if user_form.is_valid():
            cd = user_form.cleaned_data

            user = authenticate(
                username=cd['username'],
                password=cd['password']
            )
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Siz tizimga muvaffaqityatli kirdingiz! ✅")
                    return redirect('journal:main_page')
                else:
                    messages.warning(request, "Foydalanuvchi faol emas! ⚠️")
                    return redirect('users:login')
            else:
                messages.error(request, "Bunday foydalanuvchi mavjud emas! ❌",
                               extra_tags="danger")
                return redirect('users:login')
    else:
        user_form = LoginForm()

    return render(request, 'registration/login.html',
                  {'form': user_form})


@login_required
def profile(request: HttpRequest):
#     get_or_save_statistic(request)
    return render(request, 'users/_profile.html',
                  {'user': request.user,
                   'profile': request.profile})


@login_required
def user_logout(request: HttpRequest):
    logout(request)
    messages.info(request, "Siz tizimdan chiqdingiz ❗️❗️")
    return redirect('users:login')


@login_required
def profile_update(request: HttpRequest):
#     get_or_save_statistic(request)
    user = request.user
    profile = request.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileCreateForm(data=request.POST, instance=profile,
                                         files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Profil muvaffaqiyatli o'zgartirildi!")
            return redirect('users:profile')
        else:
            messages.error(request, "Iltimos, to'g'ri ma'lumotlar kiriting!")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileCreateForm(instance=profile)

    return render(request,
                  'users/profile_update.html',
                  context={
                      'user_form': user_form,
                      'profile_form': profile_form
                  })



