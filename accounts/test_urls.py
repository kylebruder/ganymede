from .models import User
from django.test import Client, TestCase
from django.urls import reverse

class TestUrlStatus(TestCase):

    client = Client()

    def assertResponse(self, pattern='home', status=200):
        '''
        A method to test the response to a GET request
        given a pattern and a status code to compare it too
        returns the client response
        '''
        response = self.client.get(reverse(pattern))
        self.assertEqual(response.status_code, status)
        return response

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', 
            email=None, 
            password='testpassword'
        )

    def test_urls(self):
        self.assertResponse(pattern='accounts:login')
        self.assertResponse(pattern='accounts:logout', status=302)

    def test_urls_logged_in(self):
        self.client.login(username='test', password='testpassword')
        self.assertTrue(self.user.is_authenticated)
        self.assertResponse(pattern='accounts:login')
        self.assertResponse(pattern='accounts:logout', status=302)

    def tearDown(self):
        self.client.logout()
