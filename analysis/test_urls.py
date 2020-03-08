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
        self.assertResponse(pattern='analysis:upload', status=302)
        self.assertResponse(pattern='analysis:create_meta_report', status=302)
        self.assertResponse(pattern='analysis:metareport_list', status=302)
        self.assertResponse(pattern='analysis:create_report', status=302)
        self.assertResponse(pattern='analysis:enter_well_data', status=302)
        self.assertResponse(pattern='analysis:report_list', status=302)

    def test_urls_logged_in(self):
        self.client.login(username='test', password='testpassword')
        self.assertTrue(self.user.is_authenticated)
        self.assertResponse(pattern='analysis:upload')
        self.assertResponse(pattern='analysis:create_meta_report')
        self.assertResponse(pattern='analysis:metareport_list')
        self.assertResponse(pattern='analysis:create_report')
        self.assertResponse(pattern='analysis:enter_well_data')
        self.assertResponse(pattern='analysis:report_list')

    def tearDown(self):
        self.client.logout()
