from django.contrib.sitemaps import Sitemap
from .models import Article

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # Arxivlanmagan barcha maqolalarni qaytaramiz
        return Article.objects.filter(is_archived=False).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at
