from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from journal.sitemaps import ArticleSitemap

sitemaps = {
    'articles': ArticleSitemap,
}
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

from django.contrib.auth import views as auth_views

from django.http import HttpResponse

def google_verify(request):
    return HttpResponse("google-site-verification: google180c3dd409d01067.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('journal.urls', namespace='journal')),
    # path('', include('users.urls', namespace='users')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('google180c3dd409d01067.html', google_verify),

    path('password-change/', auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('password-reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
] + i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('journal.urls', namespace='journal')),
    path('', include('users.urls', namespace='users')),
)

from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
