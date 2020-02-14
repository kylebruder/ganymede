
# analysis/views.py
from datetime import datetime
from pytz import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    )
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.files.images import ImageFile
from matplotlib import pyplot as plt
from .forms import UploadFileForm, DateRangeSelector, MetaReportSelector
from .models import Well, WellReading, WellReport, Unit, MetaReport
from io import TextIOWrapper, BytesIO 
import os
import csv
import numpy as np
import pandas as pd

pd.plotting.register_matplotlib_converters()
# Create your views here.

class FileFieldView(LoginRequiredMixin, FormView):
    # View for the mulitple file upload form
    # Allows a user to upload csv files to be converted to django models
    form_class = UploadFileForm
    template_name = 'analysis/upload.html'
    success_url = reverse_lazy('analysis:upload')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            for f in files:
                try:
                    wr = WellReading
                    wr.handle_csv_file(wr, request, f, f.name)
                except:
                    messages.error(
                        request,
                        '{} could not be read'.format(
                            f.name
                        )
                    )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class CreateMetaReport(LoginRequiredMixin, FormView):
    # View to create a report based on a date range
    form_class = MetaReportSelector
    template_name = 'analysis/createmetareport.html'
    success_url = reverse_lazy('analysis:metareport_list')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            mr = MetaReport
            mr.export_csv(mr, request, form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class MetaReportListView(LoginRequiredMixin, ListView):
    model = MetaReport
    paginate_by = 100
    ordering = ['-creation_date']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class MetaReportDetailView(LoginRequiredMixin, DetailView):
    model = MetaReport
    template_name = 'analysis/metareport_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CreateWellReport(LoginRequiredMixin, FormView):
    # View to create a report based on a date range
    form_class = DateRangeSelector
    template_name = 'analysis/createwellreport.html'
    success_url = reverse_lazy('analysis:report_list')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            wr = WellReport
            wr.analyze_by_date(wr, request, form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class WellReportListView(LoginRequiredMixin, ListView):
    model = WellReport
    paginate_by = 100
    ordering = ['-creation_date']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class WellReportDetailView(LoginRequiredMixin, DetailView):
    model = WellReport
    template_name = 'analysis/wellreport_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CreateWellReading(LoginRequiredMixin, CreateView):
    model = WellReading
    template_name = 'analysis/wellreading_create_form.html'
    fields = [
        'well',
        'date',
        'value',
        'unit',
        'tag_comments',
    ]
    
    def get_success_url(self):
        return reverse_lazy('analysis:enter_well_data') 

