from django.db.models import Sum
from .models import About, SendingArticle, Article


def admin_context(request):
    about = About.objects.first()
    sending = SendingArticle.objects.first()

    article_count  = Article.objects.count()
    total_views    = Article.objects.aggregate(v=Sum('views'))['v'] or 0
    author_set     = (
        Article.objects
        .exclude(authors__isnull=True)
        .exclude(authors='')
        .values_list('authors', flat=True)
    )
    # Rough unique author count by splitting comma-separated names
    unique_authors = set()
    for a in author_set:
        for name in a.split(','):
            n = name.strip()
            if n:
                unique_authors.add(n.lower())

    return {
        'global_about':    about,
        'global_sending':  sending,
        'stat_articles':   article_count,
        'stat_views':      total_views,
        'stat_authors':    len(unique_authors),
    }
