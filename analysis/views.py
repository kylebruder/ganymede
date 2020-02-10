
# analysis/views.py
from datetime import datetime
from pytz import timezone#
from django.conf import settings#
from django.contrib import messages#
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
from matplotlib import pyplot as plt#
from .forms import UploadFileForm, DateRangeSelector, MetaReportSelector
from .models import Well, WellReading, WellReport, Unit, MetaReport
from io import TextIOWrapper, BytesIO #
import os#
import csv#
import numpy as np#
import pandas as pd#

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
                #try:
                wr = WellReading
                wr.handle_csv_file(wr, request, f, f.name)
                #except:
                #    messages.error(
                #        request,
                #        '{} could not be read'.format(
                #            f.name
                #        )
                #    )
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

##### View functions #####

#
#def export_csv(request, form):
    #'''
    #Takes a POST request and form object containing data that will be used for
    #creating a MetaReport containing a CSV file.
    #Looks for the following keys in form.cleaned_data:
    #units - a list of choices from a MultipleModelChoice form field
    #start_date - an entry from a DateTimeField form field
    #end_date - an entry from a DateTimeField form field
    #'''
    ## Get the wells specified in the form data
    #wells = Well.objects.all()
    #units = form.cleaned_data['units']
    ## Set model parameters here
    #start_date = form.cleaned_data['start_date']
    #end_date = form.cleaned_data['end_date']
    #dt_format = "%x"
    #report_context="All wells"
    #report_title=report_context + " from {} to {}".format(
            #start_date.strftime(dt_format), 
            #end_date.strftime(dt_format),
    #)
    ## Create the path where the CSV file will live
    #media_dir = datetime.now().strftime("media/%Y/%m/%d/")
    #dest_dir = os.path.join(
        #settings.BASE_DIR,
        #media_dir
    #)
    #try:
        #os.makedirs(dest_dir)
    #except:
        #print('{} could not be created!'.format(dest_dir)) 
    #filename = report_title.replace(" ", "_").replace("/", ".") + str(datetime.now().time()) + ".csv"
    #dest_path = dest_dir + filename
    ## Initialize the CSV file and header
    #csv_file = open(dest_path, 'w', newline='')
    #csv_writer = csv.writer(
        #csv_file, 
        #delimiter=',',
        #quotechar='|',
        #quoting=csv.QUOTE_MINIMAL,
    #)
    #csv_writer.writerow([
        #"Well",
        #"Units",
        #"Start",
        #"End",
        #"First Reading",
        #"First Date",
        #"Last Reading",
        #"Last Date",
        #"Min",
        #"Max",
        #"Mean",
    #])
    ## Perform the analysis for each well
    #for well in wells:
        #w = Well.objects.get(name=well)
        #for unit in units:
            #u = Unit.objects.get(name=unit)
            ## Match well readings that match the well and the unit
            ## and fall within the date range
            ## Each time this loop runs it adds a line to the CSV file
            #matched_readings = WellReading.objects.filter(
                #well=w,
                #date__range=(start_date, end_date),
                #unit=u
            #)
            ## Prepare date for Pandas and NumPy
            #values = []
            #dates = []
            #try:
                #first_date = matched_readings.earliest('date').date
                #last_date = matched_readings.latest('date').date
            #except:
                #pass
            #for reading in matched_readings:
                #values.append(reading.value)
                #dates.append(reading.date.strftime(dt_format))
            #if len(values) == len(dates):
                #pass
            #else:
                #print("Warning: Number of values does not match number of dates")
            ## Get the statistics
            #if values:
                #mean = np.mean(values)
                #minimum = min(values)
                #maximum = max(values)
                #first = values[0]
                #last = values[-1]
                ## Write the line to the CSV file
                #csv_writer.writerow([
                    #str(w),
                    #str(u),
                    #start_date.strftime(dt_format),
                    #end_date.strftime(dt_format),
                    #first,
                    #first_date.strftime(dt_format),
                    #last,
                    #last_date.strftime(dt_format),
                    #minimum,
                    #maximum,
                    #mean,
                #])
    ## Create a MetaReport 
    ##try:
    #meta_report, created = MetaReport.objects.get_or_create(
        #user=request.user,
        #title=report_title,
        #start_date=start_date,
        #end_date=end_date,
        #csv= datetime.now().strftime("%Y/%m/%d/") + filename
    #)
    #csv_file.close()
    ##except:
    ##    pass
#
#def analyze_by_date(request, form):
    #'''
    #Takes a POST request and form object containing data that will be used for
    #creating WellReport objects.
    #Looks for the following keys in form.cleaned_data:
    #wells - a list of choices from MultipleModelChoice form field
    #units - a list of choices from a MultipleModelChoice form field
    #start_date - an entry from a DateTimeField form field
    #end_date - an entry from a DateTimeField form field
    #'''
    ## Get the wells specified in the form data
    #wells = form.cleaned_data['wells']
    #units = form.cleaned_data['units']
    #start_date = form.cleaned_data['start_date']
    #end_date = form.cleaned_data['end_date']
    ## Perform the analysis for each well
    #for well in wells:
        ##print(type(well))
        #w = Well.objects.get(name=well)
        ##print(w)
        #for unit in units:
            #u = Unit.objects.get(name=unit)
            ## Match well readings match the well
            ## and fall within the date range
            ## and match the unit
            #matched_readings = WellReading.objects.filter(
                #well=w,
                #date__range=(start_date, end_date),
                #unit=u
            #)
            ## Prepare date for MatPlot and NumPy
            #values = []
            #dates = []
            #mr_count = matched_readings.count() - 1
            #try:
                #first_date = matched_readings.earliest('date').date
            #except:
                #pass
            #try:
                #last_date = matched_readings.latest('date').date
            #except:
                #pass
            #for reading in matched_readings:
                #values.append(reading.value)
                #dates.append(reading.date.strftime("%x"))
            #if len(values) == len(dates):
                ##for i in range(len(values)):
                ##    print('{} :{}'.format(values[i], dates[i]))
                #pass
            #else:
                #print("number of values does not match number of dates")
            ## Get the statistics
            #if values:
                #mean = np.mean(values)
                #minimum = min(values)
                #maximum = max(values)
                #first = values[0]
                #last = values[-1]
                ## Create a WellReport model instance for each file
                #dt_format = "%x"
                #report_title='{} {} in {}'.format(
                    #w, 
                    #u.measurement_type.title(),
                    #u.name,
                    #first_date.strftime(dt_format), 
                    #last_date.strftime(dt_format)
                #)
                #report, created = WellReport.objects.get_or_create(
                    #well=w,
                    #user=request.user,
                    #title=report_title + ' from {} to {}'.format(
                        #first_date.strftime(dt_format), 
                        #last_date.strftime(dt_format)
                    #),
                    #start_date=start_date,
                    #end_date=end_date,
                    #unit=u,
                    #mean=mean,
                    #minimum=minimum,
                    #maximum=maximum,
                    #first=first,
                    #first_date=first_date,
                    #last=last,
                    #last_date=last_date,
                #)
                ## Create the graph
                ## Create the path where the graph will live
                #dti = pd.DatetimeIndex(dates)
                #df = pd.Series(values, index=dti)
                #print(dti.freq) 
                #
                #dest_dir = os.path.join(
                    #settings.BASE_DIR,
                    #datetime.now().strftime("media/%Y/%m/%d/")
                #)
                #try:
                    #os.makedirs(dest_dir)
                #except:
                    #pass
#
                #dest_path = dest_dir+str(report.pk)+".png"
                #
                #plt = make_double_sma_time_fig(df, u.name, 5, 10, report_title)
                #plt.savefig(dest_path)
                #plt.close()    
#
                #if report:
                    #report.graph = datetime.now().strftime(
                        #"media/%Y/%m/%d/"
                    #)+str(report.pk)+".png"
                    #report.save()
            #else:
                #print('There was no data for {}'.format(w))
#
#def make_double_sma_time_fig(
    #df, 
    #units='units', 
    #sma1=20, 
    #sma2=60, 
    #title='Untitled'
    #):
    #'''
    #A helper function to make a time series graph with two moving averages.
#
    #Keyword Arguments:
    #df -- a data frame object
    #units -- a string to be used to label the y axis
    #sma1 -- the number of periods for the first moving average
    #sma2 -- the number of periods for the second moving average
    #title -- the title of the graph
    #'''
    #
    #
    #plt.plot(df, label=units)
    #plt.plot(
        #df.rolling(
            #sma1, 
            #min_periods=1, 
            #center=True
        #).mean(), 
        #label='{} value SMA'.format(sma1)
    #)
    #plt.plot(
        #df.rolling(
            #sma2, 
            #min_periods=5, 
            #center=True
        #).mean(), 
        #label='{} value SMA'.format(sma2)
    #)
    #plt.hlines(df.mean(), df.index[0], df.index[-1], linestyle='--', label='mean')
    #plt.xlabel("Date")
    #plt.ylabel(units)
    #plt.title(title)
    #plt.legend()
    #plt.tick_params(axis='x', rotation=45)
    #plt.tight_layout()
    #return plt
#
#def handle_csv_file(request, in_file, name='file'):
    #'''
    #Handles an uploaded file from a POST request by
    #getting or creating the following model objects:
    #* Well
    #* Unit
    #* WellReading
    #The objects must be imported from analysis.models 
    #when calling this function.
    #The name of the well is derived from the begining of the filename.
    #The units are derived from column D [3] in the header.
    #The WellReadings are created based on the datetime and value;
    #columns A [0] and D [3] 
    #
#
    #Keyword arguments:
    #request -- POST request object
    #in_file -- CSV formatted file
    #name -- the filename
    #'''
    ## Get or create a Well object based on the begining of the filename
    #well_name=name.strip('.csv').rsplit('_')[0]
    ##try:
    #well, created = Well.objects.get_or_create(
        #name=well_name,
        #location="undisclosed"
    #)
    ##except:
    ##    messages.error(
    ##        request,
    ##        'Failed to create new Well object for {}'.format(name)
    ##    )
#
    ## Get the unit type from the file name
    ## Convert in memory bytestream in to text
    #fo = TextIOWrapper(in_file, encoding=request.encoding)
    ## Create models out of the uploaded files
    #reader = csv.reader(fo)
    #headers = next(reader)
    ## Keep track of the line number
    #line = 1
    #unit_name, metric = get_unit_type(headers[3])
#
    ## Get or create a Unit object based on the value header
    #try:
        #unit, created = Unit.objects.get_or_create(
            #name=unit_name,
            #measurement_type=metric
        #)
    #except:
        #unit = None
#
    #for row in reader:
        ## Increment line number
        #line += 1
        ## From each row, attempt to extract values to be entered into 
        ## the WellReading Model
        ## If it errors, send a message to the view and set
        ## the variable to None
        ## Extract date
        #try:
            #date = timezone('US/Pacific').localize(pd.to_datetime(row[0]))
        #except:
            #messages.error(
                #request,
                #'{}, line {} : Date could not be read'.format(
                    #name, 
                    #line
                #)
            #)
            #date = None
        ## Extract value
        #try:
            #value = float(row[3])
        #except:
            #messages.error(
                #request,
                #'{}, line {} : Value could not be read'.format(
                    #name, 
                    #line
                #)
            #)
            #value = None
        ## Extract Quality code
        #try:
            #code = int(row[4])
        #except:
            #messages.error(
                #request,
                #'{}, line {} : Quality Code could not be read'.format(
                    #name,
                    #line
                #)
            #)
            #code = None    
        ## Extract Tag Comments
        #try:
            #comments = str(row[7])
        #except:
            #messages.error(
                #request, 
                #'{}, line {} : Tag Coments could not be read'.format(
                    #name,
                    #line
                #)
            #)
            #comments = None    
        #
        ## Attempt to create a WellReading object based on the extracted data
        #try:
            #well_reading, created = WellReading.objects.get_or_create(
                #origin_file=name,
                #well=well, 
                #date=date,
                #unit=unit,
                #value=value,
                #quality_code=code,
                #tag_comments=comments,
            #)
            ## If a line is tagged with "ug" convert micrograms to milligrams
            #if (
                #'ug/L' in well_reading.tag_comments 
                #or 'ppb' in well_reading.tag_comments
            #):
                #micro_grams = well_reading.value
                #well_reading.value = micro_grams / 1000
                #well_reading.save()
        #except:
            #messages.error(
                #request,
                #'Line {} in {} was not read into the model'.format(
                     #line,
                     #name
                #)
            #) 
#
#def get_unit_type(string):
    #'''
    #Given a string, ascertain the unit type.
    #Returns unit, metric as strings.
    #'''
    #if "milligram per litre" in string:
        #unit = 'mg/L'
        #metric = 'chloride content'
    #elif 'foot' in string:
        #unit = 'feet'
        #metric = 'height'
    #else:
        #unit = 'units'
        #metric = ''
    #return unit, metric
