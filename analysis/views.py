
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
from .forms import UploadFileForm, DateRangeSelector
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
                    handle_csv_file(request, f, f.name)
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

class CreateWellReport(LoginRequiredMixin, FormView):
    # View to create a report based on a date range
    form_class = DateRangeSelector
    template_name = 'analysis/createwellreport.html'
    success_url = reverse_lazy('analysis:create_report')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            analyze_by_date(request, form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class WellReportListView(LoginRequiredMixin, ListView):
    model = WellReport
    paginate_by = 100
    #template_name = 'analysis/wellreport_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['now'] = timezone.now()
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

##### View functions #####

def analyze_by_date(request, form):
    '''
    Takes a POST request and form object containing data that will be used for
    creating WellReport objects.
    Looks for the following keys in form.cleaned_data:
    wells - a list of choices from MultipleModelChoice form field
    units - a list of choices from a MultipleModelChoice form field
    start_date - an entry from a DateTimeField form field
    end_date - an entry from a DateTimeField form field
    '''
    # Get the wells specified in the form data
    wells = form.cleaned_data['wells']
    units = form.cleaned_data['units']
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    # Perform the analysis for each well
    for well in wells:
        #print(type(well))
        w = Well.objects.get(name=well)
        #print(w)
        for unit in units:
            u = Unit.objects.get(name=unit)
            # Match well readings match the well
            # and fall within the date range
            # and match the unit
            matched_readings = WellReading.objects.filter(
                well=w,
                date__range=(start_date, end_date),
                unit=u
            )
            # Prepare date for MatPlot and NumPy
            values = []
            dates = []
            for reading in matched_readings:
                values.append(reading.value)
                dates.append(reading.date.strftime("%x"))
            if len(values) == len(dates):
                #for i in range(len(values)):
                #    print('{} :{}'.format(values[i], dates[i]))
                pass
            else:
                print("number of values does not match number of dates")
            # Get the statistics
            if values:
                mean = np.mean(values)
                minimum = min(values)
                maximum = max(values)
                last = values[-1]
                # Create a WellReport model instance for each file
                dt_format = "%x"
                report_title='{} {} in {} from {} to {}'.format(
                    w, 
                    u.measurement_type,
                    u.name,
                    start_date.strftime(dt_format), 
                    end_date.strftime(dt_format)
                )
                report, created = WellReport.objects.get_or_create(
                    well=w,
                    user=request.user,
                    title=report_title,
                    start_date=start_date,
                    end_date=end_date,
                    unit=u,
                    mean=mean,
                    minimum=minimum,
                    maximum=maximum,
                    last=last
                )
                # Create the graph
                # Create the path where the graph will live
                dest_dir = os.path.join(
                    settings.BASE_DIR,
                    datetime.now().strftime("media/%Y/%m/%d/")
                )
                try:
                    os.makedirs(dest_dir)
                except:
                    pass

                dest_path = dest_dir+str(report.pk)+".png"
                plt.bar(dates, values, width=1, color="blue")
                plt.xlabel("Date")
                plt.ylabel(unit)
                plt.title(report_title)
                plt.tick_params(axis='x', rotation=45)
                # Only label every other tick on the x axis
                #for label in plt.axes().xaxis.get_ticklabels()[::2]:
                #    label.set_visible(False)
                plt.tight_layout()
                plt.savefig(dest_path)
                plt.close()    

                if report:
                    report.graph = datetime.now().strftime(
                        "media/%Y/%m/%d/"
                    )+str(report.pk)+".png"
                    report.save()
            else:
                print('There was no data for {}'.format(w))

def handle_csv_file(request, in_file, name='file'):
    '''
    Handles an uploaded file from a POST request by
    getting or creating several model objects.
    Returns nothing.

    Keyword arguments:
    request -- POST request object
    in_file -- CSV formatted file
    name -- the filename
    '''
    # Get or create a Well object based on the begining of the filename
    well_name=name.strip('.csv').rsplit('_')[0]
    #try:
    well, created = Well.objects.get_or_create(
        name=well_name,
        location="undisclosed"
    )
    #except:
    #    messages.error(
    #        request,
    #        'Failed to create new Well object for {}'.format(name)
    #    )

    # Get the unit type from the file name
    unit_name, metric = get_unit_type(name)

    # Get or create a Unit object based on the begining of the filename
    try:
        unit, created = Unit.objects.get_or_create(
            name=unit_name,
            measurement_type=metric
        )
    except:
        unit = None

    # Convert in memory bytestream in to text
    fo = TextIOWrapper(in_file, encoding=request.encoding)
    # Create models out of the uploaded files
    reader = csv.reader(fo)
    next(reader)
    # Keep track of the line number
    line = 1
    for row in reader:
        # Increment line number
        line += 1
        # From each row, attempt to extract values to be entered into 
        # the WellReading Model
        # If it errors, send a message to the view and set
        # the variable to None
        # Extract date
        try:
            date = timezone('US/Pacific').localize(pd.to_datetime(row[0]))
        except:
            messages.error(
                request,
                '{}, line {} : Date could not be read'.format(
                    name, 
                    line
                )
            )
            date = None
        # Extract value
        try:
            value = float(row[3])
        except:
            messages.error(
                request,
                '{}, line {} : Value could not be read'.format(
                    name, 
                    line
                )
            )
            value = None
        # Extract Quality code
        try:
            code = int(row[4])
        except:
            messages.error(
                request,
                '{}, line {} : Quality Code could not be read'.format(
                    name,
                    line
                )
            )
            code = None    
        # Extract Tag Comments
        try:
            comments = str(row[7])
        except:
            messages.error(
                request, 
                '{}, line {} : Tag Coments could not be read'.format(
                    name,
                    line
                )
            )
            comments = None    
        
        # Attempt to create a WellReading object based on the extracted data
        try:
            well_reading, created = WellReading.objects.get_or_create(
                origin_file=name,
                well=well, 
                date=date,
                unit=unit,
                value=value,
                quality_code=code,
                tag_comments=comments,
            )
            # If a line is tagged with "ug" convert micrograms to milligrams
            if (
                'ug/L' in well_reading.tag_comments 
                or 'ppb' in well_reading.tag_comments
            ):
                micro_grams = well_reading.value
                well_reading.value = micro_grams / 1000
                well_reading.save()
        except:
            messages.error(
                request,
                'Line {} in {} was not read into the model'.format(
                     line,
                     name
                )
            ) 

def get_unit_type(string):
    '''
    Given a filename in string format, ascertain the unit type.
    Returns unit, metric as strings.
    '''
    if '_CL' in string:
        unit = 'mg/L'
        metric = 'chloride content'
    elif '_WL' in string:
        unit = 'feet'
        metric = 'height'
    else:
        unit = 'units'
        metric = ''
    return unit, metric
