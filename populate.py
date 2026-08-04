import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from journal.models import YearCategory, Journal, Article, Category

def populate():
    # Kategoriya yaratish (agar kerak bo'lsa)
    cat, _ = Category.objects.get_or_create(name="Texnologiyalar", defaults={'slug': 'texnologiyalar'})
    
    # 1. Yil yaratish
    year, created = YearCategory.objects.get_or_create(
        year=2024,
        defaults={'is_active': True}
    )
    if created:
        print("2024-yil qo'shildi.")
    else:
        print("2024-yil allaqachon mavjud.")
        
    # 2. Jurnal (Katta maqola) yaratish
    journal, created = Journal.objects.get_or_create(
        year_category=year,
        source_number=1,
        defaults={
            'image': '',
            'file': ''
        }
    )
    if created:
        print("2024-yil 1-sonli jurnal qo'shildi.")
    else:
        print("2024-yil 1-sonli jurnal allaqachon mavjud.")
        
    # 3. Maqola qo'shish
    article, created = Article.objects.get_or_create(
        title="Sun'iy intellektning ta'limdagi o'rni",
        defaults={
            'slug': 'suniy-intellektning-talimdagi-orni',
            'content': '<p>Bu maqolada sun\'iy intellektning ta\'limdagi ahamiyati haqida so\'z boradi. Bu namunaviy maqola.</p>',
            'category': cat,
            'journal': journal,
            'authors': 'Aliyev Vali',
        }
    )
    if created:
        print("Namunaviy maqola qo'shildi.")
    else:
        print("Namunaviy maqola allaqachon mavjud.")

if __name__ == "__main__":
    populate()
