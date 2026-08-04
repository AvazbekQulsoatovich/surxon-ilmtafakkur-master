from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField

from utils.models import BaseModel

User = get_user_model()


class YearCategory(BaseModel):
    year = models.IntegerField(unique=True, verbose_name="Yil")
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-year']
        verbose_name_plural = 'year categories'

    def __str__(self):
        return str(self.year)

    def get_update_url(self):
        return reverse('journal:year_update', kwargs={'id': self.pk})

    def get_delete_url(self):
        return reverse('journal:year_delete', kwargs={'id': self.pk})


class Journal(BaseModel):
    image = models.ImageField(upload_to='journal/images/%Y/%m/%d/', blank=True, null=True)
    file = models.FileField(upload_to='journal/files/%Y/%m/%d/',
                            validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])], blank=True, null=True)

    year_category = models.ForeignKey(YearCategory, on_delete=models.CASCADE, related_name='journals', null=True, blank=True)
    source_number = models.SmallIntegerField()

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])
        ]

    def __str__(self):
        year = self.year_category.year if self.year_category else "N/A"
        return f'Journal({year}-{self.source_number})'

    def get_update_url(self):
        return reverse('journal:journal_update',
                       kwargs={
                           'id': self.pk
                       })

    def get_delete_url(self):
        return reverse('journal:journal_delete',
                       kwargs={
                           'id': self.pk
                       })


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    color = models.CharField(max_length=20, default='#1b3a6b')

    objects = models.Manager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('journal:article_list') + f'?category={self.slug}'


class Article(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True,
                            unique_for_date='created_at')
    content = RichTextField(blank=True, null=True)
    doi = models.CharField(max_length=255, blank=True, null=True, verbose_name="DOI")
    pages = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sahifalar (masalan: 84-91)")
    abstract = RichTextField(blank=True, null=True, verbose_name="Annotatsiya (Abstract)")
    keywords = models.CharField(max_length=500, blank=True, null=True, verbose_name="Kalit so'zlar (Keywords)")
    references = RichTextField(blank=True, null=True, verbose_name="Foydalanilgan adabiyotlar (References)")
    pdf_file = models.FileField(upload_to='articles/pdfs/%Y/%m/%d/',
                                validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
                                blank=True, null=True, verbose_name="PDF yoki DOC fayl")
    views = models.IntegerField(default=0, editable=False)
    authors = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='articles'
    )
    journal = models.ForeignKey(
        'Journal', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='articles',
        verbose_name="Jurnal soni"
    )
    is_archived  = models.BooleanField(default=False)
    ai_summary   = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('journal:article_detail',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })

    def get_update_url(self):
        return reverse('journal:article_update',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })

    def get_delete_url(self):
        return reverse('journal:article_delete',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })

class ArticleFile(BaseModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to='articles/pdfs/%Y/%m/%d/', validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])])
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title or self.pdf_file.name


class Editorial(BaseModel):
    image = models.ImageField(upload_to='journal/images/%Y/%m/%d/', blank=True, null=True)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    position = models.CharField(max_length=150, default='')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
        verbose_name = "Tahririyat a'zosi"
        verbose_name_plural = "Tahririyat a'zolari"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('journal:editorial_list', )

    def get_update_url(self):
        return reverse('journal:editorial_update',
                       kwargs={
                           'id': self.pk
                       })

    def get_delete_url(self):
        return reverse('journal:editorial_delete',
                       kwargs={
                           'id': self.pk
                       })


class Post(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True,
                            unique_for_date='created_at')

    content = RichTextField()
    # image = models.ImageField(upload_to='image/%Y/%m/%d/',
    #                           blank=True, null=True)
    mediaImage = models.FileField(upload_to='media/%Y/%m/%d/',
                                  validators=[
                                      FileExtensionValidator(['mp4', 'avi', 'mpeg', 'webm', 'png', 'jpeg', 'jpg', ])],
                                  blank=True, null=True)
    file_extension = models.CharField(max_length=10, blank=True, null=True)

    views = models.IntegerField(default=0, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts',
                               blank=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('journal:post_detail',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })

    def get_update_url(self):
        return reverse('journal:post_update',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })

    def get_delete_url(self):
        return reverse('journal:post_delete',
                       kwargs={
                           'slug': self.slug,
                           'id': self.pk
                       })


class ArticleBand(BaseModel):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='bands')
    title   = models.CharField(max_length=255, default='Band')
    content = models.TextField(blank=True, default='')
    order   = models.PositiveSmallIntegerField(default=1)

    objects = models.Manager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.article.title} – {self.title}'


class Contact(BaseModel):
    message = models.TextField(blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL,
                               blank=True, null=True)
    is_read = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        return str(self.is_read)


class About(BaseModel):
    content = RichTextField()

    journal_name = models.CharField(max_length=127)
    journal_image = models.ImageField(upload_to='journal/about/images/%Y/%m/%d/')

    author_description = RichTextField()
    author_image = models.ImageField(upload_to='journal/about/images/%Y/%m/%d/')

    objects = models.Manager()


class SendingArticle(BaseModel):
    content = RichTextField()

    objects = models.Manager()


class SitePage(BaseModel):
    class PageType(models.TextChoices):
        MAXFIYLIK = 'maxfiylik', "Maxfiylik siyosati"
        NASHR = 'nashr', "Nashr etiketkasi"

    page_type = models.CharField(
        max_length=20,
        choices=PageType.choices,
        unique=True,
        verbose_name="Sahifa turi"
    )
    content = RichTextField(verbose_name="Kontent (asosiy)")
    content_uz = RichTextField(blank=True, null=True, verbose_name="Kontent (O'zbek)")
    content_en = RichTextField(blank=True, null=True, verbose_name="Kontent (Ingliz)")
    content_ru = RichTextField(blank=True, null=True, verbose_name="Kontent (Rus)")

    objects = models.Manager()

    class Meta:
        verbose_name = "Sayt sahifasi"
        verbose_name_plural = "Sayt sahifalari"

    def __str__(self):
        return self.get_page_type_display()


class SocialMedia(BaseModel):
    class SocialMediaChoice(models.TextChoices):
        FACEBOOK = 'facebook',
        TWITTER = 'twitter'
        LINKEDIN = 'linkedin'
        YOUTUBE = 'youtube'
        TELEGRAM = 'telegram'
        WHATSAPP = 'whatsapp'
        INSTAGRAM = 'instagram'
        GITHUB = 'github'

    class ColorChoice(models.TextChoices):
        RED = 'red'
        GREEN = 'green'
        BLUE = 'blue'
        PURPLE = 'purple'
        BLACK = 'black'
        WHITE = 'white'

    title = models.CharField(max_length=31, choices=SocialMediaChoice.choices,
                             unique=True)
    color = models.CharField(max_length=31, choices=ColorChoice.choices)
    url = models.URLField(max_length=255)

    objects = models.Manager()

    def __str__(self):
        return self.title

    def get_update_url(self):
        return reverse('journal:social_media_update',
                       kwargs={
                           'id': self.pk
                       })

    def get_delete_url(self):
        return reverse('journal:social_media_delete',
                       kwargs={
                           'id': self.pk
                       })


class Submission(BaseModel):
    class StatusChoice(models.TextChoices):
        PENDING = 'pending', "Kutilmoqda"
        REVIEWING = 'reviewing', "Taqriz jarayonida"
        ACCEPTED = 'accepted', "Qabul qilindi"
        REJECTED = 'rejected', "Rad etildi"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])]
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING
    )
    feedback = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author.username}"


