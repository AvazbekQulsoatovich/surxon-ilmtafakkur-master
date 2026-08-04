from django.contrib import admin
from django import forms
from . import models


class SitePageAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('content', 'content_uz'):
            self.fields[field_name].widget = forms.Textarea(attrs={
                'rows': 10,
                'style': 'width: 100%;',
            })

    class Meta:
        model = models.SitePage
        fields = '__all__'


@admin.register(models.SitePage)
class SitePageAdmin(admin.ModelAdmin):
    form = SitePageAdminForm
    list_display = ('page_type', 'created_at', 'updated_at')
    list_display_links = ('page_type',)
    search_fields = ('content',)
    fields = ('page_type', 'content', 'content_uz')


@admin.register(models.YearCategory)
class YearCategoryAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_active', 'created_at')
    search_fields = ('year',)
    list_filter = ('is_active', 'created_at')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}



@admin.register(models.Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('file', 'year_category', 'source_number',
                    'created_at', 'updated_at')
    search_fields = ('source_number', 'year_category')
    list_filter = ('created_at', 'updated_at')


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'views', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'mediaImage', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = ('sender', 'message', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('sender',)
    search_fields = ('message',)


@admin.register(models.About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('content', 'journal_image', 'author_image', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'journal_image', 'author_image')

@admin.register(models.SendingArticle)
class SendingArticleAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content',)

@admin.register(models.Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('image', 'first_name', 'last_name', 'position', 'phone_number', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'position')
    list_display_links = ('first_name', 'last_name')


@admin.register(models.SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'created_at', 'updated_at')


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'abstract', 'author__username')
    raw_id_fields = ('author',)


