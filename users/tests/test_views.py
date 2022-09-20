from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class RegisterViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.page_name = reverse(viewname='users:register')
        cls.user = {
            'email': 'test@ya.ru',
            'password1': 'TestPass12',
            'password2': 'TestPass12',
        }
        cls.user_short_password = {
            'email': 'test@ya.ru',
            'password1': 'Test',
            'password2': 'Test'
        }
        cls.user_different_passwords = {
            'email': 'test@ya.ru',
            'password1': 'TestPass12',
            'password2': 'TestPass15'
        }

    def setUp(self):
        self.get_response = self.client.get(self.page_name)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/my/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.assertEqual(self.get_response.status_code, 200)

    def test_view_use_correct_template(self):
        self.assertEqual(self.get_response.status_code, 200)
        self.assertTemplateUsed(self.get_response, 'users/register.html')

    def test_can_register_user(self):
        response = self.client.post(self.page_name, self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.all().count(), 1)
        self.assertEqual(CustomUser.objects.all()[0].email, 'test@ya.ru')

    def test_cant_register(self):
        response = self.client.post(self.page_name, self.user_short_password)
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.count(), 0)

        response = self.client.post(self.page_name, self.user_different_passwords)
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.count(), 0)

    # def test_redirect_after_register(self):
    #     response = self.client.post(self.page_name, self.user)
    #     self.assertRedirects(response, reverse('/'))

    def test_authenticated_after_register(self):
        self.client.post(self.page_name, self.user)
        response = self.client.get(self.page_name)
        self.assertTrue(response.context['user'].is_authenticated)


class LogInTestView(TestCase):
    data = {
        'email': 'test@ya.ru',
        'password': 'TestPass12',
    }

    @classmethod
    def setUpTestData(cls):
        cls.page_name = reverse(viewname='users:login')

    def setUp(self):
        self.get_response = self.client.get(self.page_name)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/my/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.assertEqual(self.get_response.status_code, 200)

    def test_view_use_correct_template(self):
        self.assertEqual(self.get_response.status_code, 200)
        self.assertTemplateUsed(self.get_response, 'users/login.html')


class LogOutTestView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_name = reverse(viewname='users:logout')

    def setUp(self):
        self.get_response = self.client.get(self.page_name)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/my/logout/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.assertEqual(self.get_response.status_code, 200)

    def test_view_use_correct_template(self):
        self.assertEqual(self.get_response.status_code, 200)
        self.assertTemplateUsed(self.get_response, 'users/logout.html')


class ResetPasswordTestView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_name = reverse(viewname='users:reset_password')
        CustomUser.objects.create(email='testuser@ya.ru', password='testpass123')

    def setUp(self):
        self.get_response = self.client.get(self.page_name)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/my/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.assertEqual(self.get_response.status_code, 200)

    def test_view_use_correct_template(self):
        self.assertEqual(self.get_response.status_code, 200)
        self.assertTemplateUsed(self.get_response, 'users/reset_password.html')

    def test_reset_password(self):
        response = self.client.post(self.page_name, data={'email': 'testuser@ya.ru'})
        self.assertEqual(response.status_code, 200)
        user = CustomUser.objects.get(email='testuser@ya.ru')
        self.assertTrue(user.check_password('qwerty1234'))
