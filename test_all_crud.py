import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

User = get_user_model()
client = Client()

print("--- Boshladik: CRUD Testing ---")

# 1. Login
user = User.objects.get(username='admin')
client.force_login(user)
print("1. Login: OK")

# 2. Test YearCategory
print("\n--- YearCategory Test ---")
# Create
response = client.post('/uz/year/create/', {'year': 2030, 'is_active': True})
if response.status_code in [200, 302]:
    print("YearCategory Create POST: OK", response.status_code)
else:
    print("YearCategory Create POST: ERROR", response.status_code)
    
from journal.models import YearCategory, Journal, Article, Category
year = YearCategory.objects.get(year=2030)

# Update
response = client.post(f'/uz/year/update/{year.id}/', {'year': 2031, 'is_active': True})
if response.status_code in [200, 302]:
    print("YearCategory Update POST: OK", response.status_code)
else:
    print("YearCategory Update POST: ERROR", response.status_code)

year.refresh_from_db()
print(f"Year is now: {year.year}")

# 3. Test Journal
print("\n--- Journal Test ---")
# Create
# Note: journal form has image/file fields. We made them optional. Let's see if it works without files.
response = client.post('/uz/journal/create/', {
    'year_category': year.id,
    'source_number': 99
})
if response.status_code in [200, 302]:
    print("Journal Create POST: OK", response.status_code)
else:
    print("Journal Create POST: ERROR", response.status_code, response.content.decode('utf-8')[:500])

journal = Journal.objects.get(source_number=99, year_category=year)

# Update
response = client.post(f'/uz/journal/update/{journal.id}/', {
    'year_category': year.id,
    'source_number': 100
})
if response.status_code in [200, 302]:
    print("Journal Update POST: OK", response.status_code)
else:
    print("Journal Update POST: ERROR", response.status_code)
journal.refresh_from_db()

# 4. Test Article
print("\n--- Article Test ---")
category = Category.objects.first()
# Create
response = client.post('/uz/article/create/', {
    'title': 'Test Maqola',
    'authors': 'Test Muallif',
    'year': year.id,
    'journal': journal.id,
    'doi': 'https://doi.org/10.1234/test',
    'pages': '1-10',
    'abstract': 'Test abstract',
    'category': category.id if category else ''
})
if response.status_code in [200, 302]:
    print("Article Create POST: OK", response.status_code)
else:
    print("Article Create POST: ERROR", response.status_code, response.context['form'].errors if hasattr(response, 'context') and 'form' in response.context else '')

article = Article.objects.get(title='Test Maqola')

# Update
response = client.post(f'/uz/article/update/{article.id}/', {
    'title': 'Test Maqola Updated',
    'authors': 'Test Muallif',
    'year': year.id,
    'journal': journal.id,
    'doi': 'https://doi.org/10.1234/test',
    'pages': '1-10',
    'abstract': 'Test abstract',
    'category': category.id if category else ''
})
if response.status_code in [200, 302]:
    print("Article Update POST: OK", response.status_code)
else:
    print("Article Update POST: ERROR", response.status_code)
article.refresh_from_db()

# Archive toggle
response = client.post(f'/uz/article/{article.id}/archive/')
if response.status_code in [200, 302]:
    print("Article Archive Toggle: OK", response.status_code)
else:
    print("Article Archive Toggle: ERROR", response.status_code)

# 5. Test Delete
print("\n--- Delete Tests ---")
# Article delete
response = client.post(f'/uz/article/delete/{article.id}/')
if response.status_code in [200, 302]:
    print("Article Delete POST: OK", response.status_code)
else:
    print("Article Delete POST: ERROR", response.status_code)

# Journal delete
response = client.post(f'/uz/journal/delete/{journal.id}/')
if response.status_code in [200, 302]:
    print("Journal Delete POST: OK", response.status_code)
else:
    print("Journal Delete POST: ERROR", response.status_code)

# Year delete
response = client.post(f'/uz/year/delete/{year.id}/')
if response.status_code in [200, 302]:
    print("Year Delete POST: OK", response.status_code)
else:
    print("Year Delete POST: ERROR", response.status_code)

print("\n--- Barcha testlar yakunlandi ---")
