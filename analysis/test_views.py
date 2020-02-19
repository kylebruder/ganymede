import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from analysis.models import Well, Unit, WellReport, MetaReport, WellReading
from analysis.forms import UploadFileForm
from analysis.views import (FileFieldView, MetaReportListView, 
    MetaReportDetailView, CreateWellReport, WellReportListView,
    WellReportDetailView, CreateWellReading)



class UploadFiles(TestCase):

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(username='test', email=None, password='testpassword')
        self.assertEqual(User.objects.all().count(), 1)

    def test_a_csv_file(self):
        logged_in = self.client.login(username='test', password='testpassword')
        self.assertTrue(logged_in)
        with open('static/XX-0XX_XX.csv') as f:
            response = self.client.post(reverse('analysis:upload'), {'file_field': f})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Well.objects.all().count(), 1)
