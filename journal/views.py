import io
import os
import zipfile
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from django.conf import settings

from django.http import HttpRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Journal, Post, Article, SocialMedia, About, Contact, SendingArticle, Editorial, Category, ArticleBand, SitePage, Submission
from .forms import ContactForm, ArticleForm, PostForm, JournalForm, SocialForm, AboutForm, SendingArticleForm, \
    EditorialForm, CategoryForm, SitePageForm, SubmissionForm, SubmissionReviewForm, YearCategoryForm


# from journal.functions import get_or_save_statistic


def main_page(request: HttpRequest):
    # get_or_save_statistic(request)
    posts = Post.objects.all()[:2]
    articles = Article.objects.all()[:3]

    context = {
        'posts': posts,
        'articles': articles
    }

    return render(request,
                  'journal/home.html',
                  context=context)


from .models import YearCategory

def journal_list(request: HttpRequest):
    years = YearCategory.objects.filter(is_active=True).order_by('-year')
    return render(request, 'journal/journal/list.html', {
        'years': years,
        'is_admin': _is_admin(request),
    })

def year_detail(request: HttpRequest, id):
    year_cat = get_object_or_404(YearCategory, pk=id)
    # Get all journals for this year category
    journals = year_cat.journals.all().order_by('-source_number')
    return render(request, 'journal/journal/year_detail.html', {
        'year': year_cat,
        'journals': journals,
        'is_admin': _is_admin(request),
    })

@login_required
def year_create(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = YearCategoryForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('journal:journal_list')
    else:
        form = YearCategoryForm()

    return render(request, 'journal/year/create.html', {'form': form})

@login_required
def year_update(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    year_cat = get_object_or_404(YearCategory, id=id)
    if request.method == 'POST':
        form = YearCategoryForm(instance=year_cat, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('journal:journal_list')
    else:
        form = YearCategoryForm(instance=year_cat)

    return render(request, 'journal/year/update.html', {'form': form, 'year': year_cat})

@login_required
def year_delete(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    year_cat = get_object_or_404(YearCategory, id=id)
    if request.method == 'POST':
        year_cat.delete()
        return redirect('journal:journal_list')
    return render(request, 'journal/year/delete.html', {'year': year_cat})

def journal_detail(request: HttpRequest, id):
    from django.shortcuts import get_object_or_404
    journal = get_object_or_404(Journal, pk=id)
    # Get articles belonging to this journal
    articles = journal.articles.all().order_by('created_at')

    return render(request, 'journal/journal/detail.html', {
        'journal': journal,
        'articles': articles,
        'is_admin': _is_admin(request),
    })


@login_required
def journal_create(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = JournalForm(data=request.POST,
                           files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('journal:journal_list')
    else:
        form = JournalForm()

    return render(request, 'journal/journal/create.html',
                  {'form': form})


@login_required
def journal_update(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()

    journal = get_object_or_404(Journal,
                                id=id)

    if request.method == 'POST':
        form = JournalForm(data=request.POST, instance=journal,
                           files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('journal:journal_list')
    else:
        form = JournalForm(instance=journal)

    return render(request, 'journal/journal/update.html',
                  {
                      'form': form,
                      'journal': journal
                  })


@login_required
def journal_delete(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()

    journal = get_object_or_404(Journal,
                                id=id)

    if request.method == 'POST':
        journal.delete()
        return redirect('journal:journal_list')

    return render(request, 'journal/journal/delete.html',
                  {'journal': journal})


def contact(request: HttpRequest):
    #     get_or_save_statistic(request)
    form = ContactForm()

    context = {
        'form': form
    }

    return render(request, 'journal/contact.html',
                  context=context)


@require_POST
def save_contact(request: HttpRequest):
    form = ContactForm(data=request.POST)
    if form.is_valid():

        contact = form.save(commit=False)
        if request.user.is_authenticated:
            contact.sender = request.user
            sender_username = request.user.username
            sender_email = request.user.email or 'Email yo\'q'
        else:
            contact.sender = None
            sender_username = 'Mehmon (Anonymous)'
            sender_email = 'Email yo\'q'
            
        contact.save()
        messages.success(request, 'Sizning xabaringiz muvaffaqiyatli yuborildi!  ✅')

        # Adminga email bildirishnoma yuborish
        admin_email = os.environ.get('ADMIN_EMAIL', '')
        if admin_email and settings.EMAIL_HOST_USER:
            try:
                message_text = form.cleaned_data.get('message', '')
                send_mail(
                    subject=f'Yangi xabar: {sender_username} saytdan xabar yubordi',
                    message=(
                        f'Foydalanuvchi: {sender_username}\n'
                        f'Email: {sender_email}\n\n'
                        f'Xabar:\n{message_text}\n\n'
                        f'Saytda ko\'rish: http://surxon-ilmtafakkur.uz/message/list/'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin_email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Email xatoligi asosiy jarayonni to'xtatmasin

    else:
        messages.error(request, 'Iltimos to\'g\'ri ma\'lumot kiriting! ❌', extra_tags='danger')

    return redirect('journal:contact')


@login_required
def message_list(request: HttpRequest):
    messages = Contact.objects.all().order_by('-created_at').select_related('sender', 'sender__profile')
    messages.update(is_read=True)
    messages_count = messages.count()
    paginator = Paginator(messages, 5)
    page_number = request.GET.get('page', 1)

    try:
        messages = paginator.page(page_number)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)

    return render(request, 'journal/message/list.html',
                  {
                      'messages': messages,
                      'messages_count': messages_count
                  })


@login_required
@require_POST
def message_delete_all(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    messages = Contact.objects.filter(is_read=True)
    messages.delete()
    return redirect('users:profile')


def about(request: HttpRequest):
    datas = About.objects.all().first()

    return render(request, context={'datas': datas},
                  template_name='journal/about/about.html')


def booking_article(request: HttpRequest):
    data = SendingArticle.objects.all().first()
    context = {"data": data}
    return render(request, 'journal/guide_for_authors.html', context)


def nashr_etiketkasi(request: HttpRequest):
    page = SitePage.objects.filter(page_type='nashr').first()
    return render(request, 'journal/nashr_etiketkasi.html', {
        'page': page,
        'is_admin': _is_admin(request),
    })


def maxfiylik_siyosati(request: HttpRequest):
    page = SitePage.objects.filter(page_type='maxfiylik').first()
    return render(request, 'journal/maxfiylik_siyosati.html', {
        'page': page,
        'is_admin': _is_admin(request),
    })


@login_required
def sitepage_update(request: HttpRequest, page_type):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    page, created = SitePage.objects.get_or_create(
        page_type=page_type,
        defaults={'content': ''}
    )
    if request.method == 'POST':
        form = SitePageForm(data=request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sahifa muvaffaqiyatli yangilandi! ✅')
            if page_type == 'nashr':
                return redirect('journal:nashr_etiketkasi')
            return redirect('journal:maxfiylik_siyosati')
    else:
        form = SitePageForm(instance=page)
    return render(request, 'journal/sitepage_update.html', {
        'form': form,
        'page': page,
        'page_type': page_type,
    })


def editorial_list(request: HttpRequest):
    editorials = Editorial.objects.all()
    paginator = Paginator(editorials, 14)
    page_number = request.GET.get('page', 1)

    try:
        editorials = paginator.page(page_number)
    except PageNotAnInteger:
        editorials = paginator.page(1)
    except EmptyPage:
        editorials = paginator.page(paginator.num_pages)

    return render(request, context={
        'editorials': editorials,
        'pag_start': False,
        'pag_end': False,
    }, template_name='journal/editorial/list.html')


def article_list(request: HttpRequest):
    from django.db.models import Q
    from .models import YearCategory
    categories = Category.objects.annotate(count=models.Count('articles'))
    
    year_id = request.GET.get('year', '')
    journal_id = request.GET.get('journal', '')
    category_slug = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()

    qs = Article.objects.all()
    active_category = None
    active_journal = None
    active_year = None
    
    years = YearCategory.objects.filter(is_active=True).annotate(journal_count=models.Count('journals')).order_by('-year')
    journals = Journal.objects.annotate(count=models.Count('articles'))

    if year_id:
        active_year = YearCategory.objects.filter(id=year_id).first()
        if active_year:
            journals = journals.filter(year_category=active_year)

    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            qs = qs.filter(category=active_category)
            
    if journal_id:
        active_journal = Journal.objects.filter(id=journal_id).first()
        if active_journal:
            qs = qs.filter(journal=active_journal)
            if active_journal.year_category:
                active_year = active_journal.year_category

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(authors__icontains=q) |
            Q(content__icontains=q)
        )

    paginator = Paginator(qs, 6)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, 'journal/article/list.html', {
        'articles': articles,
        'categories': categories,
        'years': years,
        'journals': journals,
        'active_category': active_category,
        'active_journal': active_journal,
        'active_year': active_year,
        'search_query': q,
        'pag_start': False,
        'pag_end': False,
    })


@login_required
@require_POST
def article_archive_toggle(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    article = get_object_or_404(Article, id=id)
    article.is_archived = not article.is_archived
    article.save(update_fields=['is_archived'])
    status = "arxivga qo'shildi" if article.is_archived else "arxivdan chiqarildi"
    messages.success(request, f'"{article.title}" {status}.')
    return redirect(request.META.get('HTTP_REFERER', 'journal:article_list'))


@login_required
@require_POST
def article_ai_summary(request: HttpRequest, id):
    article = get_object_or_404(Article, id=id)

    # Agar allaqachon mavjud bo'lsa qaytarib ber
    if article.ai_summary:
        from django.http import JsonResponse
        return JsonResponse({'summary': article.ai_summary, 'cached': True})

    from django.utils.html import strip_tags
    import anthropic as _anthropic

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        from django.http import JsonResponse
        return JsonResponse({'error': 'ANTHROPIC_API_KEY sozlanmagan'}, status=500)

    clean_text = strip_tags(article.content or '').strip()
    if len(clean_text) < 30:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Maqola matni juda qisqa'}, status=400)

    try:
        client = _anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=400,
            messages=[{
                'role': 'user',
                'content': (
                    'Quyidagi ilmiy maqolani o\'zbek tilida 3-4 jumlada qisqacha xulosa qil. '
                    'Faqat xulosani yoz, boshqa hech narsa yozma.\n\n'
                    'Maqola:\n' + clean_text[:4000]
                )
            }]
        )
        summary = msg.content[0].text.strip()
        article.ai_summary = summary
        article.save(update_fields=['ai_summary'])
        from django.http import JsonResponse
        return JsonResponse({'summary': summary, 'cached': False})
    except Exception as exc:
        from django.http import JsonResponse
        return JsonResponse({'error': str(exc)}, status=500)


def article_download(request: HttpRequest, slug, id):
    import io
    import os
    from html.parser import HTMLParser
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import HexColor

    article = get_object_or_404(Article, slug=slug, id=id)

    # 1. Register Arial Font Family for Unicode support (Windows system font)
    windir = os.environ.get('WINDIR', 'C:\\Windows')
    fonts_dir = os.path.join(windir, 'Fonts')
    
    font_files = {
        'Arial': 'arial.ttf',
        'Arial-Bold': 'arialbd.ttf',
        'Arial-Italic': 'ariali.ttf',
        'Arial-BoldItalic': 'arialbi.ttf'
    }
    
    registered = {}
    for name, filename in font_files.items():
        path = os.path.join(fonts_dir, filename)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = name
            except Exception:
                pass
                
    if 'Arial' in registered:
        pdfmetrics.registerFontFamily(
            'Arial',
            normal=registered.get('Arial'),
            bold=registered.get('Arial-Bold', registered.get('Arial')),
            italic=registered.get('Arial-Italic', registered.get('Arial')),
            boldItalic=registered.get('Arial-BoldItalic', registered.get('Arial'))
        )
        font_name = 'Arial'
    else:
        font_name = 'Helvetica'

    # 2. Setup document and styles
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = []

    # Custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name='ArticlePDFTitle',
        fontName=font_name,
        fontSize=18,
        leading=22,
        textColor=HexColor('#1b3a6b'),
        spaceAfter=12,
        alignment=1 # Center aligned
    )
    
    meta_style = ParagraphStyle(
        name='ArticlePDFMeta',
        fontName=font_name,
        fontSize=9.5,
        leading=14,
        textColor=HexColor('#555555'),
        spaceAfter=15,
        alignment=1 # Center aligned
    )
    
    body_style = ParagraphStyle(
        name='ArticlePDFBody',
        fontName=font_name,
        fontSize=10.5,
        leading=16,
        spaceAfter=12,
        textColor=HexColor('#1a1a2e')
    )

    # 3. HTML Parser to clean CKEditor content for ReportLab Paragraph
    class ReportLabHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.paragraphs = []
            self.current_paragraph = ""
            self.active_tags = []
            
        def handle_starttag(self, tag, attrs):
            if tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'li', 'ul', 'ol']:
                if self.current_paragraph.strip():
                    self.paragraphs.append(self.current_paragraph.strip())
                    self.current_paragraph = ""
            elif tag in ['b', 'strong']:
                self.current_paragraph += "<b>"
                self.active_tags.append("b")
            elif tag in ['i', 'em']:
                self.current_paragraph += "<i>"
                self.active_tags.append("i")
            elif tag in ['u']:
                self.current_paragraph += "<u>"
                self.active_tags.append("u")
            elif tag == 'a':
                href = dict(attrs).get('href', '#')
                self.current_paragraph += f'<a href="{href}" color="blue">'
                self.active_tags.append("a")
                
        def handle_endtag(self, tag):
            if tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul', 'ol']:
                if self.current_paragraph.strip():
                    self.paragraphs.append(self.current_paragraph.strip())
                    self.current_paragraph = ""
            elif tag in ['b', 'strong'] and "b" in self.active_tags:
                self.current_paragraph += "</b>"
                self.active_tags.remove("b")
            elif tag in ['i', 'em'] and "i" in self.active_tags:
                self.current_paragraph += "</i>"
                self.active_tags.remove("i")
            elif tag in ['u'] and "u" in self.active_tags:
                self.current_paragraph += "</u>"
                self.active_tags.remove("u")
            elif tag == 'a' and "a" in self.active_tags:
                self.current_paragraph += "</a>"
                self.active_tags.remove("a")
                
        def handle_data(self, data):
            escaped_data = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.current_paragraph += escaped_data
            
        def close(self):
            super().close()
            if self.current_paragraph.strip():
                self.paragraphs.append(self.current_paragraph.strip())
                self.current_paragraph = ""

    # Helper function to construct Paragraph flowables safely
    def make_paragraph(text, style):
        try:
            return Paragraph(text, style)
        except Exception:
            import re
            clean_text = re.sub(r'<[^>]+>', '', text)
            clean_text = clean_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return Paragraph(clean_text, style)

    # 4. Build PDF story
    # Title
    story.append(make_paragraph(article.title, title_style))
    story.append(Spacer(1, 4))
    
    # Metadata: Authors, Date, Category
    meta_parts = []
    if article.authors:
        meta_parts.append(f"Mualliflar: {article.authors}")
    meta_parts.append(f"Sana: {article.created_at.strftime('%d.%m.%Y')}")
    if article.category:
        meta_parts.append(f"Kategoriya: {article.category.name}")
        
    meta_text = " | ".join(meta_parts)
    story.append(make_paragraph(meta_text, meta_style))
    
    # Horizontal Rule
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#dddddd"), spaceBefore=0, spaceAfter=20))
    
    # Parse and add content
    if article.content:
        parser = ReportLabHTMLParser()
        parser.feed(article.content)
        parser.close()
        for para_text in parser.paragraphs:
            story.append(make_paragraph(para_text, body_style))
            
    # Build document
    doc.build(story)
    buf.seek(0)
    
    fname = article.slug or f"maqola-{article.id}"
    resp = HttpResponse(buf.read(), content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{fname}.pdf"'
    return resp



def editorial_detail(request: HttpRequest, id):
    editorial = get_object_or_404(Editorial, id=id)
    return render(request, context={'editorial': editorial}, template_name='journal/editorial/detail.html')


def article_detail(request: HttpRequest, slug, id):
    article = get_object_or_404(Article, slug=slug, id=id)
    article.views += 1
    article.save()
    bands = article.bands.all()
    return render(request, 'journal/article/detail.html', {
        'article': article,
        'bands': bands,
        'is_admin': _is_admin(request),
    })


def _is_admin(request):
    return request.user.is_authenticated and (
        request.user.is_superuser or (request.profile and request.profile.is_admin)
    )


@login_required
@require_POST
def article_band_add(request: HttpRequest, article_id):
    from django.http import JsonResponse
    article = get_object_or_404(Article, id=article_id)
    if not _is_admin(request):
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    last_order = article.bands.aggregate(models.Max('order'))['order__max'] or 0
    band = ArticleBand.objects.create(
        article=article,
        title=f'Band {last_order + 1}',
        content='',
        order=last_order + 1,
    )
    return JsonResponse({'id': band.id, 'title': band.title, 'order': band.order})


@login_required
@require_POST
def article_band_save(request: HttpRequest, band_id):
    import json
    from django.http import JsonResponse
    band = get_object_or_404(ArticleBand, id=band_id)
    if not _is_admin(request):
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON xato'}, status=400)
    band.title   = data.get('title',   band.title)[:255]
    band.content = data.get('content', band.content)
    band.save(update_fields=['title', 'content'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def article_band_delete(request: HttpRequest, band_id):
    from django.http import JsonResponse
    band = get_object_or_404(ArticleBand, id=band_id)
    if not _is_admin(request):
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    band.delete()
    return JsonResponse({'ok': True})


@login_required
def article_create(request: HttpRequest):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            
            if article.pdf_file and not article.content:
                import PyPDF2
                try:
                    pdf_reader = PyPDF2.PdfReader(article.pdf_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                    if extracted_text:
                        article.content = extracted_text.replace('\n', '<br>')
                        if hasattr(article, 'content_uz') and not article.content_uz:
                            article.content_uz = article.content
                        if hasattr(article, 'content_ru') and not article.content_ru:
                            article.content_ru = article.content
                        if hasattr(article, 'content_en') and not article.content_en:
                            article.content_en = article.content
                except Exception:
                    pass

            if not article.slug:
                article.slug = slugify(article.title)
            article.save()

            for f in request.FILES.getlist('additional_pdfs'):
                from journal.models import ArticleFile
                ArticleFile.objects.create(article=article, title=f.name, pdf_file=f)

            return redirect('journal:article_detail',
                            slug=article.slug,
                            id=article.id)
    else:
        form = ArticleForm()

    context = {
        'form': form
    }

    return render(request,
                  'journal/article/create.html',
                  context=context)


# @login_required
# def editorial_create(request: HttpRequest):
#     if not request.user.is_superuser:
#         return HttpResponseForbidden()
#
#     if request.method == 'POST':
#         form = EditorialForm(data=request.POST)
#         if form.is_valid():
#             editorial = form.save()
#             return redirect('journal:editorial_detail', id=editorial.id)
#     else:
#         form = EditorialForm()
#
#     return render(request, 'journal/editorial/create.html',{'form': form})
class editorial_create(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'journal/editorial/create.html'
    model = Editorial
    form_class = EditorialForm

    def get_success_url(self):
        return reverse_lazy('journal:editorial_detail', kwargs={'id': self.object.pk})

    def test_func(self):
        return self.request.user.is_superuser or self.request.profile.is_admin


@login_required
def article_update(request: HttpRequest, slug, id):
    article = get_object_or_404(Article,
                                slug=slug, id=id)

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            
            if 'pdf_file' in request.FILES and not article.content:
                import PyPDF2
                try:
                    pdf_reader = PyPDF2.PdfReader(article.pdf_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                    if extracted_text:
                        article.content = extracted_text.replace('\n', '<br>')
                        if hasattr(article, 'content_uz') and not article.content_uz:
                            article.content_uz = article.content
                        if hasattr(article, 'content_ru') and not article.content_ru:
                            article.content_ru = article.content
                        if hasattr(article, 'content_en') and not article.content_en:
                            article.content_en = article.content
                except Exception:
                    pass

            article.save()

            for f in request.FILES.getlist('additional_pdfs'):
                from journal.models import ArticleFile
                ArticleFile.objects.create(article=article, title=f.name, pdf_file=f)

            return redirect('journal:article_detail',
                            slug=article.slug,
                            id=article.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'journal/article/update.html',
                  {'form': form,
                   'article': article})


@login_required
def editorial_update(request: HttpRequest, id):
    editorial = get_object_or_404(Editorial, id=id)

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = EditorialForm(data=request.POST, instance=editorial)
        if form.is_valid():
            editorial = form.save()
            return redirect('journal:editorial_detail', id=editorial.id)
    else:
        form = EditorialForm(instance=editorial)
        context = {'form': form, 'editorial': editorial}

    return render(request, 'journal/editorial/update.html', context=context)


@login_required
def about_article_update(request: HttpRequest, id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    about = get_object_or_404(About, id=id)

    if request.method == 'POST':
        forma = AboutForm(data=request.POST, instance=about, files=request.FILES)
        if forma.is_valid():
            forma.save()
            return redirect('journal:about_journal')
    else:
        forma = AboutForm(instance=about)

    return render(request, template_name='journal/about/update.html',
                  context={'forma': forma, 'about': about})


@login_required
def dashboard(request: HttpRequest):
    is_super = request.user.is_superuser
    is_admin = getattr(request, 'profile', None) and request.profile.is_admin

    if not (is_super or is_admin):
        return HttpResponseForbidden()

    User = request.user.__class__
    context = {
        'article_count': Article.objects.count(),
        'post_count': Post.objects.count(),
        'journal_count': Journal.objects.count(),
        'message_count': Contact.objects.filter(is_read=False).count(),
        'editorial_count': Editorial.objects.count(),
        'articles': Article.objects.all()[:8],
        'posts': Post.objects.all()[:8],
        'journals': Journal.objects.all()[:6],
        'editorials': Editorial.objects.all()[:8],
        'messages': Contact.objects.all()[:10],
        'users': User.objects.all()[:10] if is_super else None,
        'user_count': User.objects.count() if is_super else 0,
        'is_super': is_super,
    }
    return render(request, 'journal/dashboard/index.html', context)


@login_required
def sending_article_update(request: HttpRequest, id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    article = get_object_or_404(SendingArticle, id=id)

    if request.method == 'POST':
        form = SendingArticleForm(data=request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('journal:booking_article', )
    else:
        form = SendingArticleForm(instance=article)
    context = {'form': form, 'article': article}
    return render(request, template_name='journal/guide_for_update.html', context=context)


@login_required
def article_delete(request: HttpRequest, slug, id):
    article = get_object_or_404(Article,
                                slug=slug,
                                id=id)
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        article.delete()
        return redirect('journal:article_list')

    return render(request, 'journal/article/delete.html',
                  {'article': article})


@login_required
def editorial_delete(request: HttpRequest, id):
    editorial = get_object_or_404(Editorial, id=id)

    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        editorial.delete()
        return redirect('journal:editorial_list')

    return render(request, 'journal/editorial/delete.html', {'editorial': editorial})


@login_required
def social_media_list(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    social_media = SocialMedia.objects.all()

    return render(request, 'journal/social/list.html',
                  {'social_media': social_media})


@login_required
def social_media_create(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = SocialForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('journal:social_media_list')
    else:
        form = SocialForm()

    return render(request, ''
                           'journal/social/create.html',
                  {'form': form})


@login_required
def social_media_update(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    social_media = get_object_or_404(SocialMedia, id=id)

    if request.method == 'POST':
        form = SocialForm(data=request.POST, instance=social_media)
        if form.is_valid():
            form.save()
            return redirect('journal:social_media_list')
    else:
        form = SocialForm(instance=social_media)

    return render(request, ''
                           'journal/social/update.html',
                  {
                      'form': form,
                      'social': social_media
                  })


@login_required
def social_media_delete(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()

    social_media = get_object_or_404(SocialMedia, id=id)
    if request.method == 'POST':
        social_media.delete()
        return redirect('users:profile')

    return render(request, 'journal/social/delete.html',
                  {'social': social_media})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'journal/post/list.html'
    paginate_by = 2

    # def get_context_data(self, **kwargs):
    #     get_or_save_statistic(self.request)
    #     return super().get_context_data(**kwargs)


# class PostDetailView(DetailView):
#
#     model = Post
#     context_object_name = 'post'
#     template_name = 'journal/post/detail.html'
#
#     def get(self, request, *args, **kwargs):
#         try:
#             article = self.get_object()
#             article.views += 1
#             article.save()
#             return super().get(request, *args, **kwargs)
#         except Http404:
#             # Handle case where no Post object is found
#             raise Http404("Post does not exist")

def PostDetailView(request: HttpRequest, slug, id):
    #     get_or_save_statistic(request)
    post = get_object_or_404(Post,
                             slug=slug,
                             id=id)
    post.views += 1
    post.save()

    return render(request, 'journal/post/detail.html',
                  {'post': post})


from django.utils.text import slugify


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'journal/post/create.html'
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('journal:post_list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        if not instance.slug:
            instance.slug = slugify(instance.title)
        instance.save()
        self.object = instance
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

    def test_func(self):
        return self.request.user.is_superuser or self.request.profile.is_admin


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'journal/post/update.html'
    pk_url_kwarg = 'id'

    def test_func(self):
        return self.request.user.is_superuser or self.request.profile.is_admin


# class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Post
#     template_name = 'journal/post/delete.html'
#     context_object_name = 'post'
#     success_url = reverse_lazy('journal:post_list')
#
#     def test_func(self):
#         return self.request.profile.is_admin


@login_required
def PostDeleteView(request: HttpRequest, slug, id):
    post = get_object_or_404(Post, slug=slug, id=id)
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        post.delete()
        return redirect('journal:post_list')
    return render(request, 'journal/post/delete.html', {'post': post})


# ──────────────────────────────────────────────────────────
#  KATEGORIYALAR
# ──────────────────────────────────────────────────────────
@login_required
def category_list(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    cats = Category.objects.annotate(count=models.Count('articles'))
    return render(request, 'journal/category/list.html', {'categories': cats})


@login_required
def category_create(request: HttpRequest):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya qo'shildi!")
            return redirect('journal:category_list')
    else:
        form = CategoryForm()
    return render(request, 'journal/category/create.html', {'form': form})


@login_required
def category_update(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    cat = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya yangilandi!")
            return redirect('journal:category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'journal/category/update.html', {'form': form, 'category': cat})


@login_required
def category_delete(request: HttpRequest, id):
    if not (request.user.is_superuser or request.profile.is_admin):
        return HttpResponseForbidden()
    cat = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, "Kategoriya o'chirildi!")
        return redirect('journal:category_list')
    return render(request, 'journal/category/delete.html', {'category': cat})



@login_required
def submit_article(request: HttpRequest):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.author = request.user
            submission.save()
            messages.success(request, "Maqola muvaffaqiyatli tahririyatga yuborildi! ✅")
            return redirect('journal:my_submissions')
        else:
            messages.error(request, "Xatolik yuz berdi. Iltimos qaytadan tekshirib ko'ring! ⚠️")
    else:
        form = SubmissionForm()
    return render(request, 'journal/dashboard/submit_article.html', {'form': form})


@login_required
def my_submissions(request: HttpRequest):
    submissions = Submission.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'journal/dashboard/my_submissions.html', {'submissions': submissions})


@login_required
def submission_list(request: HttpRequest):
    if not _is_admin(request):
        return HttpResponseForbidden()
    submissions = Submission.objects.all().order_by('-created_at')
    return render(request, 'journal/dashboard/submission_list.html', {
        'submissions': submissions,
        'is_admin': True
    })


@login_required
def submission_review(request: HttpRequest, id):
    if not _is_admin(request):
        return HttpResponseForbidden()
    sub = get_object_or_404(Submission, id=id)
    if request.method == 'POST':
        form = SubmissionReviewForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, "Taqriz va maqola holati yangilandi! ✅")
            return redirect('journal:submission_list')
    else:
        form = SubmissionReviewForm(instance=sub)
    return render(request, 'journal/dashboard/submission_review.html', {
        'submission': sub,
        'form': form
    })

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def api_create_year(request):
    try:
        data = json.loads(request.body)
        year_val = int(data.get('year'))
        year_obj, created = YearCategory.objects.get_or_create(year=year_val)
        return JsonResponse({'success': True, 'id': year_obj.id, 'text': str(year_obj.year)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def api_create_journal(request):
    try:
        data = json.loads(request.body)
        year_id = int(data.get('year_id'))
        source_number = int(data.get('source_number'))
        year_obj = YearCategory.objects.get(id=year_id)
        journal_obj, created = Journal.objects.get_or_create(year_category=year_obj, source_number=source_number)
        return JsonResponse({'success': True, 'id': journal_obj.id, 'text': str(journal_obj)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def submission_publish(request: HttpRequest, id):
    if not _is_admin(request):
        return HttpResponseForbidden()
    sub = get_object_or_404(Submission, id=id)
    if sub.status != Submission.StatusChoice.ACCEPTED:
        messages.error(request, "Faqat Qabul qilingan maqolalarni nashr qilish mumkin! ⚠️")
        return redirect('journal:submission_list')
    
    author_name = f"{sub.author.first_name} {sub.author.last_name}".strip()
    if not author_name:
        author_name = sub.author.username
        
    article = Article.objects.create(
        title=sub.title,
        content=f"<p><strong>Annotatsiya:</strong> {sub.abstract}</p>",
        authors=author_name,
    )
    
    messages.success(request, f"Maqola muvaffaqiyatli jurnallar safiga nashr etildi! ✅ Uni tahrirlashingiz mumkin.")
    return redirect(article.get_update_url())

