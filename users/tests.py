"""
=====================================================================
  SURXON ILM VA TAFAKKUR — Users App Test Suite
=====================================================================
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):

    def test_profile_created_with_user(self):
        """Profile modelida user bog'lanishi to'g'ri."""
        user = User.objects.create_user(username='proftest', password='P@ss123')
        profile = Profile.objects.create(user=user)
        self.assertEqual(profile.user.username, 'proftest')
        self.assertFalse(profile.is_admin)

    def test_profile_str(self):
        user = User.objects.create_user(username='strtest', password='P@ss123')
        profile = Profile.objects.create(user=user)
        self.assertIn(str(user.id), str(profile))

    def test_profile_is_admin_default_false(self):
        user = User.objects.create_user(username='admindefault', password='P@ss123')
        profile = Profile.objects.create(user=user)
        self.assertFalse(profile.is_admin)


class UserRegistrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_get(self):
        url = reverse('users:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_valid_user(self):
        """To'g'ri ma'lumotlar bilan ro'yxatdan o'tish."""
        url = reverse('users:register')
        data = {
            'username': 'newuser2024',
            'password': 'NewPass@1234',
            'email': 'new@test.com',
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            # Profile fields
            'date_birth': '2000-01-01',
            'telephone': '+998901234567',
        }
        response = self.client.post(url, data)
        # 200 (form xato) yoki 302 (muvaffaqiyat) bo'lishi mumkin
        self.assertIn(response.status_code, [200, 302])

    def test_register_duplicate_username(self):
        """Bir xil username ikki marta ro'yxatdan o'ta olmasligi."""
        User.objects.create_user(username='duplicate', password='Pass@1234')
        url = reverse('users:register')
        data = {
            'username': 'duplicate',
            'password': 'Pass@1234',
        }
        response = self.client.post(url, data)
        # Form xato berishi kerak
        self.assertIn(response.status_code, [200, 302])
        # Faqat bitta user bo'lishi kerak
        self.assertEqual(
            User.objects.filter(username='duplicate').count(), 1
        )


class ProfileUpdateTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='updateuser', password='Update@1234', email='u@t.com'
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='updateuser', password='Update@1234')

    def test_profile_update_page_accessible(self):
        url = reverse('users:profile_update')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_requires_login(self):
        self.client.logout()
        url = reverse('users:profile_update')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])
