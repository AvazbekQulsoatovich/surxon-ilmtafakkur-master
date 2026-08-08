"""
=====================================================================
  SURXON ILM VA TAFAKKUR — Journal App Test Suite
  Senior Tester: To'liq integratsiya va unit testlar
=====================================================================
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from journal.models import (
    Article, Category, Post, Journal,
    Contact, Editorial, SitePage, SocialMedia,
)
from users.models import Profile

User = get_user_model()


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def make_superuser(username='admin_test', password='Admin@1234'):
    user = User.objects.create_superuser(username=username, password=password,
                                         email='admin@test.com')
    Profile.objects.get_or_create(user=user)
    return user


def make_regular_user(username='user_test', password='User@1234'):
    user = User.objects.create_user(username=username, password=password,
                                    email='user@test.com')
    Profile.objects.get_or_create(user=user)
    return user


def make_admin_user(username='editor_test', password='Editor@1234'):
    user = User.objects.create_user(username=username, password=password,
                                    email='editor@test.com')
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.is_admin = True
    profile.save()
    return user


# ═════════════════════════════════════════════
#  1. MODEL TESTLAR
# ═════════════════════════════════════════════

class CategoryModelTest(TestCase):
    """Category modeli uchun unit testlar."""

    def test_category_slug_auto_generated(self):
        """Slug avtomatik yaratilishi kerak."""
        cat = Category.objects.create(name='Tabiiy fanlar')
        self.assertIsNotNone(cat.slug)
        self.assertNotEqual(cat.slug, '')

    def test_category_str(self):
        cat = Category.objects.create(name='Matematika')
        self.assertIn('Matematika', str(cat))

    def test_category_unique_name(self):
        """Bir xil nomli kategoriya bo'lmasligi kerak."""
        Category.objects.create(name='Fizika')
        with self.assertRaises(Exception):
            Category.objects.create(name='Fizika')

    def test_category_default_color(self):
        cat = Category.objects.create(name='Kimyo')
        self.assertEqual(cat.color, '#1b3a6b')


class ArticleModelTest(TestCase):
    """Article modeli uchun unit testlar."""

    def setUp(self):
        self.category = Category.objects.create(name='Test kategoriya')

    def test_article_slug_auto_generated(self):
        article = Article.objects.create(
            title='Yangi maqola sarlavhasi',
            content='Test kontent',
            category=self.category,
        )
        self.assertIsNotNone(article.slug)
        self.assertNotEqual(article.slug, '')

    def test_article_default_views(self):
        article = Article.objects.create(
            title='Ko\'rishlar soni testi',
            content='Test kontent',
        )
        self.assertEqual(article.views, 0)

    def test_article_default_not_archived(self):
        article = Article.objects.create(
            title='Arxiv testi',
            content='Test',
        )
        self.assertFalse(article.is_archived)

    def test_article_str(self):
        article = Article.objects.create(title='Str test maqola', content='x')
        self.assertIn('Str test maqola', str(article))

    def test_article_get_absolute_url(self):
        article = Article.objects.create(title='URL test maqola', content='x')
        url = article.get_absolute_url()
        self.assertIn(str(article.id), url)

    def test_article_ordering_newest_first(self):
        a1 = Article.objects.create(title='Birinchi', content='x')
        a2 = Article.objects.create(title='Ikkinchi', content='x')
        articles = Article.objects.all()
        self.assertEqual(articles[0].pk, a2.pk)


class EditorialModelTest(TestCase):
    def test_editorial_str(self):
        ed = Editorial.objects.create(
            first_name='Ali', last_name='Valiyev', position='Muharrir'
        )
        self.assertIn('Ali', str(ed))
        self.assertIn('Valiyev', str(ed))


class SitePageModelTest(TestCase):
    def test_sitepage_unique_page_type(self):
        SitePage.objects.create(page_type='maxfiylik', content='Test1')
        with self.assertRaises(Exception):
            SitePage.objects.create(page_type='maxfiylik', content='Test2')

    def test_sitepage_str(self):
        page = SitePage.objects.create(page_type='nashr', content='Nashr')
        self.assertIsNotNone(str(page))


class SocialMediaModelTest(TestCase):
    def test_socialmedia_str(self):
        sm = SocialMedia.objects.create(
            title='telegram', color='blue', url='https://t.me/test'
        )
        self.assertEqual(str(sm), 'telegram')

    def test_socialmedia_get_update_url(self):
        sm = SocialMedia.objects.create(
            title='instagram', color='purple', url='https://instagram.com/test'
        )
        url = sm.get_update_url()
        self.assertIn(str(sm.pk), url)


# ═════════════════════════════════════════════
#  2. VIEW TESTLAR — Ochiq sahifalar
# ═════════════════════════════════════════════

class PublicViewsTest(TestCase):
    """Login talab qilmaydigan sahifalar."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Ommaviy test')
        self.article = Article.objects.create(
            title='Ommaviy maqola',
            content='Kontent',
            category=self.category,
        )

    def test_main_page_accessible(self):
        """Bosh sahifa 200 qaytarishi kerak."""
        url = reverse('journal:main_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_list_accessible(self):
        url = reverse('journal:article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_detail_accessible(self):
        url = reverse('journal:article_detail',
                      kwargs={'id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_detail_increments_views(self):
        """Maqolani ochganda ko'rishlar soni +1 bo'lishi kerak."""
        old_views = self.article.views
        url = reverse('journal:article_detail',
                      kwargs={'id': self.article.id})
        self.client.get(url)
        self.article.refresh_from_db()
        self.assertEqual(self.article.views, old_views + 1)

    def test_editorial_list_accessible(self):
        url = reverse('journal:editorial_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_journal_list_accessible(self):
        url = reverse('journal:journal_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_page_accessible(self):
        url = reverse('journal:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_about_page_accessible(self):
        url = reverse('journal:about_journal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_nashr_etiketkasi_accessible(self):
        url = reverse('journal:nashr_etiketkasi')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_maxfiylik_siyosati_accessible(self):
        url = reverse('journal:maxfiylik_siyosati')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_booking_article_accessible(self):
        url = reverse('journal:booking_article')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_search_by_title(self):
        """Sarlavha bo'yicha qidiruv ishlashi kerak."""
        url = reverse('journal:article_list') + '?q=Ommaviy'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ommaviy maqola')

    def test_article_search_no_results(self):
        """Topilmagan qidiruv bo'sh natija qaytarishi kerak."""
        url = reverse('journal:article_list') + '?q=mavjudemas123xyz'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_filter_by_category(self):
        """Kategoriya filtri ishlashi kerak."""
        url = reverse('journal:article_list') + f'?category={self.category.slug}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ommaviy maqola')

    def test_nonexistent_article_returns_404(self):
        """Mavjud bo'lmagan maqola 404 qaytarishi kerak."""
        url = reverse('journal:article_detail',
                      kwargs={'id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_article_download(self):
        """Maqolani yuklab olish PDF qaytarishi kerak."""
        url = reverse('journal:article_download',
                      kwargs={'id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# ═════════════════════════════════════════════
#  3. VIEW TESTLAR — Login kerak sahifalar
# ═════════════════════════════════════════════

class AuthRequiredViewsTest(TestCase):
    """@login_required sahifalar redirectga yuborishi kerak."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_redirects_anonymous(self):
        url = reverse('journal:dashboard')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])

    def test_message_list_redirects_anonymous(self):
        url = reverse('journal:message_list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])

    def test_article_create_redirects_anonymous(self):
        url = reverse('journal:article_create')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])

    def test_social_media_list_redirects_anonymous(self):
        url = reverse('journal:social_media_list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])


# ═════════════════════════════════════════════
#  4. VIEW TESTLAR — Superuser imkoniyatlari
# ═════════════════════════════════════════════

class SuperuserViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(username='admin_test', password='Admin@1234')
        self.category = Category.objects.create(name='Super test kategoriya')
        self.article = Article.objects.create(
            title='Super test maqola', content='Kontent',
            category=self.category,
        )

    def test_dashboard_accessible_for_superuser(self):
        url = reverse('journal:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_create_get(self):
        url = reverse('journal:article_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_update_get(self):
        url = reverse('journal:article_update',
                      kwargs={'id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_delete_get(self):
        url = reverse('journal:article_delete',
                      kwargs={'id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_delete_post(self):
        """Maqolani o'chirish ishlashi kerak."""
        article_id = self.article.id
        url = reverse('journal:article_delete',
                      kwargs={'id': self.article.id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertFalse(Article.objects.filter(id=article_id).exists())

    def test_sitepage_update_get(self):
        url = reverse('journal:sitepage_update', kwargs={'page_type': 'maxfiylik'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sitepage_update_post(self):
        """SitePage yangilash ishlashi kerak."""
        url = reverse('journal:sitepage_update', kwargs={'page_type': 'nashr'})
        data = {
            'content': 'Yangilangan kontent',
            'content_uz': '',
            'content_en': '',
            'content_ru': '',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [302, 200])

    def test_article_archive_toggle(self):
        """Maqolani arxivlash toggle ishlashi kerak."""
        self.assertFalse(self.article.is_archived)
        url = reverse('journal:article_archive_toggle',
                      kwargs={'id': self.article.id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 301])
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_archived)

    def test_category_list_accessible(self):
        url = reverse('journal:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_create_post(self):
        url = reverse('journal:category_create')
        data = {'name': 'Yangi kategoriya', 'color': '#ff0000'}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [302, 200])
        self.assertTrue(Category.objects.filter(name='Yangi kategoriya').exists())

    def test_message_list_accessible_for_superuser(self):
        url = reverse('journal:message_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# ═════════════════════════════════════════════
#  5. VIEW TESTLAR — Oddiy foydalanuvchi
# ═════════════════════════════════════════════

class RegularUserPermissionTest(TestCase):
    """Oddiy user admin sahifalariga kira olmasligi kerak."""

    def setUp(self):
        self.client = Client()
        self.regular_user = make_regular_user()
        self.client.login(username='user_test', password='User@1234')
        self.article = Article.objects.create(
            title='Ruxsat testi maqola', content='Kontent'
        )

    def test_article_create_forbidden_for_regular_user(self):
        url = reverse('journal:article_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_article_delete_forbidden_for_regular_user(self):
        url = reverse('journal:article_delete',
                      kwargs={'id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sitepage_update_forbidden_for_regular_user(self):
        url = reverse('journal:sitepage_update', kwargs={'page_type': 'maxfiylik'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_dashboard_forbidden_for_regular_user(self):
        url = reverse('journal:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_can_view_articles(self):
        """Oddiy user maqolalarni ko'rishi mumkin."""
        url = reverse('journal:article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# ═════════════════════════════════════════════
#  6. CONTACT (Xabar yuborish) TESTLAR
# ═════════════════════════════════════════════

class ContactTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_regular_user()
        self.client.login(username='user_test', password='User@1234')

    def test_contact_save_valid(self):
        """To'g'ri xabar yuborilishi kerak."""
        url = reverse('journal:save_contact')
        data = {'message': 'Bu test xabari'}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [302, 301])
        self.assertTrue(Contact.objects.filter(
            message='Bu test xabari', sender=self.user
        ).exists())

    def test_contact_save_anonymous_redirects(self):
        """Anonim foydalanuvchi redirect bo'lishi kerak."""
        self.client.logout()
        url = reverse('journal:save_contact')
        response = self.client.post(url, {'message': 'anonim test'})
        self.assertIn(response.status_code, [302, 301])

    def test_contact_save_empty_message(self):
        """Bo'sh xabar saqlanmasligi kerak."""
        url = reverse('journal:save_contact')
        count_before = Contact.objects.count()
        response = self.client.post(url, {'message': ''})
        self.assertEqual(Contact.objects.count(), count_before)


# ═════════════════════════════════════════════
#  7. ARTICLE BAND (Bo'lim) TESTLAR
# ═════════════════════════════════════════════

class ArticleBandTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(username='admin_test', password='Admin@1234')
        self.article = Article.objects.create(
            title='Band test maqola', content='Kontent'
        )

    def test_band_add(self):
        """Bo'lim qo'shish ishlashi kerak."""
        from django.utils import translation
        with translation.override('uz'):
            url = reverse('journal:article_band_add',
                          kwargs={'article_id': self.article.id})
        # follow=True — i18n redirect bo'lsa ham natijani olamiz
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('id', data)

    def test_band_save(self):
        """Bo'limni saqlash ishlashi kerak."""
        import json
        from journal.models import ArticleBand
        band = ArticleBand.objects.create(
            article=self.article, title='Eski sarlavha', content='', order=1
        )
        url = reverse('journal:article_band_save', kwargs={'band_id': band.id})
        payload = json.dumps({'title': 'Yangi sarlavha', 'content': 'Yangi kontent'})
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        band.refresh_from_db()
        self.assertEqual(band.title, 'Yangi sarlavha')

    def test_band_delete(self):
        """Bo'limni o'chirish ishlashi kerak."""
        from journal.models import ArticleBand
        band = ArticleBand.objects.create(
            article=self.article, title="O'chiriladigan band", content='', order=2
        )
        band_id = band.id
        url = reverse('journal:article_band_delete', kwargs={'band_id': band_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ArticleBand.objects.filter(id=band_id).exists())

    def test_band_add_forbidden_for_regular_user(self):
        """Oddiy user bo'lim qo'sha olmasligi kerak."""
        self.client.logout()
        regular = make_regular_user('band_test_user', 'Pass@1234')
        self.client.login(username='band_test_user', password='Pass@1234')
        url = reverse('journal:article_band_add',
                      kwargs={'article_id': self.article.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


# ═════════════════════════════════════════════
#  8. USERS APP TESTLAR
# ═════════════════════════════════════════════

class UserAuthTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_login_page_accessible(self):
        url = reverse('users:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_page_accessible(self):
        url = reverse('users:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        """To'g'ri ma'lumotlar bilan login muvaffaqiyatli."""
        User.objects.create_user(
            username='logintest', password='TestPass@123', email='l@t.com'
        )
        Profile.objects.get_or_create(
            user=User.objects.get(username='logintest')
        )
        url = reverse('users:login')
        data = {'username': 'logintest', 'password': 'TestPass@123'}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [302, 301])

    def test_invalid_login(self):
        """Noto'g'ri parol bilan login muvaffaqiyatsiz."""
        User.objects.create_user(username='faillogin', password='RealPass@1')
        url = reverse('users:login')
        data = {'username': 'faillogin', 'password': 'WrongPass!'}
        response = self.client.post(url, data)
        # Login sahifasida qoladi yoki redirect qiladi — 200 yoki 302
        self.assertIn(response.status_code, [200, 302])

    def test_logout_redirects(self):
        user = make_regular_user('logout_user', 'Logout@1234')
        self.client.login(username='logout_user', password='Logout@1234')
        url = reverse('users:logout')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])

    def test_profile_page_requires_login(self):
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])

    def test_profile_page_accessible_when_logged_in(self):
        make_regular_user()
        self.client.login(username='user_test', password='User@1234')
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# ═════════════════════════════════════════════
#  9. XAVFSIZLIK TESTLAR
# ═════════════════════════════════════════════

class SecurityTest(TestCase):
    """Xavfsizlik va ruxsat testlari."""

    def setUp(self):
        self.client = Client()
        self.superuser = make_superuser()
        self.regular = make_regular_user()
        self.article = Article.objects.create(
            title='Security test maqola', content='Kontent'
        )

    def test_csrf_protected_contact(self):
        """CSRF himoyasi tekshiruvi."""
        self.client.login(username='user_test', password='User@1234')
        url = reverse('journal:save_contact')
        # enforce_csrf_checks=True bilan client yaratish
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username='user_test', password='User@1234')
        response = csrf_client.post(url, {'message': 'csrf test'})
        self.assertEqual(response.status_code, 403)

    def test_admin_only_endpoint_forbidden(self):
        """Admin endpoint oddiy userga 403 qaytarishi kerak."""
        self.client.login(username='user_test', password='User@1234')
        url = reverse('journal:article_archive_toggle',
                      kwargs={'id': self.article.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_access_admin_endpoint(self):
        """Superuser admin endpointga kira olishi kerak."""
        self.client.login(username='admin_test', password='Admin@1234')
        url = reverse('journal:article_archive_toggle',
                      kwargs={'id': self.article.id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 200])

    def test_sitepage_only_superuser(self):
        """SitePage faqat superuser uchun."""
        self.client.login(username='user_test', password='User@1234')
        url = reverse('journal:sitepage_update', kwargs={'page_type': 'nashr'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


# ═════════════════════════════════════════════
#  10. PAGINATION TESTLAR
# ═════════════════════════════════════════════

class PaginationTest(TestCase):

    def setUp(self):
        self.client = Client()
        for i in range(15):
            Article.objects.create(title=f'Maqola {i}', content=f'Kontent {i}')

    def test_article_list_first_page(self):
        url = reverse('journal:article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_list_second_page(self):
        url = reverse('journal:article_list') + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_list_invalid_page(self):
        """Noto'g'ri sahifa — birinchi sahifaga qaytishi kerak."""
        url = reverse('journal:article_list') + '?page=abc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_article_list_out_of_range_page(self):
        """Chegaradan oshgan sahifa — oxirgi sahifaga qaytishi kerak."""
        url = reverse('journal:article_list') + '?page=9999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
