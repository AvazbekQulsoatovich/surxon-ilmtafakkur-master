from django.urls import path
from . import views

app_name = 'journal'




urlpatterns = [
    path('', views.main_page, name='main_page'),

    path('contact/', views.contact, name='contact'),
    path('save_contact/', views.save_contact, name='save_contact'),

    path('editorial/list/', views.editorial_list, name='editorial_list'),
    path('editorial/<int:id>/', views.editorial_detail, name='editorial_detail'),
    path('editorial/update/<int:id>/', views.editorial_update, name='editorial_update'),
    path('editorial/delete/<int:id>/', views.editorial_delete,
         name='editorial_delete'),
    path('editorial/create/', views.editorial_create.as_view(), name='editorial_create'),


    path('article/list/', views.article_list, name='article_list'),
    path('article/<slug:slug>/<int:id>/',
         views.article_detail, name='article_detail'),
    path('article/update/<slug:slug>/<int:id>/',
         views.article_update, name='article_update'),
    path('article/delete/<slug:slug>/<int:id>/', views.article_delete,
         name='article_delete'),
    path('article/create/', views.article_create, name='article_create'),
    path('article/<int:id>/archive/', views.article_archive_toggle, name='article_archive_toggle'),
    path('article/<slug:slug>/<int:id>/download/', views.article_download, name='article_download'),
    path('article/<int:id>/ai-summary/', views.article_ai_summary, name='article_ai_summary'),
    path('article/<int:article_id>/band/add/', views.article_band_add, name='article_band_add'),
    path('article/band/<int:band_id>/save/', views.article_band_save, name='article_band_save'),
    path('article/band/<int:band_id>/delete/', views.article_band_delete, name='article_band_delete'),

    path('post/list/',
         views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/<int:id>/',
         views.PostDetailView, name='post_detail'),
    path('post/update/<slug:slug>/<int:id>/',
         views.PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<slug:slug>/<int:id>/',
         views.PostDeleteView, name='post_delete'),
    path('post/create/', views.PostCreateView.as_view(),
         name='post_create'),

    path('year/create/', views.year_create, name='year_create'),
    path('year/<int:id>/', views.year_detail, name='year_detail'),
    path('year/update/<int:id>/', views.year_update, name='year_update'),
    path('year/delete/<int:id>/', views.year_delete, name='year_delete'),

    path('journal/list/', views.journal_list, name='journal_list'),
    path('journal/<int:id>/', views.journal_detail, name='journal_detail'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/update/<int:id>/', views.journal_update, name='journal_update'),
    path('journal/delete/<int:id>/', views.journal_delete, name='journal_delete'),

    path('social/list/', views.social_media_list, name='social_media_list'),
    path('social/update/<int:id>/', views.social_media_update, name='social_media_update'),
    path('social/delete/<int:id>/', views.social_media_delete, name='social_media_delete'),
    path('social/create/', views.social_media_create, name='social_media_create'),

    path('message/list/', views.message_list, name='message_list'),
    path('message/delete/all/', views.message_delete_all, name='message_delete_all'),

    path('journal/about/', views.about, name='about_journal'),
    path('journal/about/<int:id>/', views.about_article_update, name='about_article_update'),
    path('booking/article/', views.booking_article, name='booking_article'),
    path('booking/article/<int:id>/', views.sending_article_update, name='sending_article_update'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('category/list/', views.category_list, name='category_list'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/update/<int:id>/', views.category_update, name='category_update'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),

    path('nashr-etiketkasi/', views.nashr_etiketkasi, name='nashr_etiketkasi'),
    path('maxfiylik-siyosati/', views.maxfiylik_siyosati, name='maxfiylik_siyosati'),
    path('sitepage/update/<str:page_type>/', views.sitepage_update, name='sitepage_update'),

    # Maqolalar yuborish kabineti
    path('dashboard/submit-article/', views.submit_article, name='submit_article'),
    path('dashboard/my-submissions/', views.my_submissions, name='my_submissions'),
    path('dashboard/submissions/', views.submission_list, name='submission_list'),
    path('dashboard/submission/<int:id>/review/', views.submission_review, name='submission_review'),
    path('dashboard/submission/<int:id>/publish/', views.submission_publish, name='submission_publish'),

    # APIs for dynamic creation
    path('api/create-year/', views.api_create_year, name='api_create_year'),
    path('api/create-journal/', views.api_create_journal, name='api_create_journal'),
]
