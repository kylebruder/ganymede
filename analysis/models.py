
# analysis/models.py
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from io import TextIOWrapper, BytesIO
from matplotlib import pyplot as plt
from pytz import timezone as ptz
import os
import csv
import numpy as np
import pandas as pd
# Create your models here.


class Unit(models.Model):
    name = models.CharField(max_length=256, default="unit")
    measurement_type = models.CharField(max_length=256, default=None)
    
    def __str__(self):
        return self.name

class Well(models.Model):
    name = models.CharField(max_length=256, default=None)
    location = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.name

class WellReport(models.Model):
    well = models.ForeignKey(Well, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, default='untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    graph = models.ImageField(upload_to='reports/%Y/%m/%d/', default=None)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    mean = models.FloatField(default=None)
    minimum= models.FloatField(default=None)
    maximum = models.FloatField(default=None)
    first = models.FloatField(default=None)
    first_date = models.DateTimeField(null=True)
    last = models.FloatField(default=None)
    last_date = models.DateTimeField(null=True)
    total_readings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('analysis:report_detail',
            args=[str(self.id)]
        )

    def make_double_sma_time_fig(
        self,
        df,
        units='units',
        sma1=20,
        sma2=60,
        title='Untitled',
        total_values=0,
        ):
        '''
        A helper function to make a time series graph with two moving averages.
    
        Keyword Arguments:
        df -- a data frame object
        units -- a string to be used to label the y axis
        sma1 -- the number of periods for the first moving average
        sma2 -- the number of periods for the second moving average
        title -- the title of the graph
        total_values -- the total amount of values; used to determine
            whether or not to display moving averages
        '''
    
    
        plt.plot(df, label=units)
        if total_values >= sma1:
            plt.plot(
                df.rolling(
                    sma1,
                    min_periods=1,
                    center=True
                ).mean(),
                label='{} value SMA'.format(sma1)
            )
        if total_values >= sma2:
            plt.plot(
                df.rolling(
                    sma2,
                    min_periods=1,
                    center=True
                ).mean(),
                label='{} value SMA'.format(sma2)
            )
        plt.hlines(df.mean(), df.index[0], df.index[-1], linestyle='--', label='mean')
        plt.xlabel("Date")
        plt.ylabel(units)
        plt.title(title)
        plt.legend()
        plt.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        return plt

    def analyze_by_date(self, request, form):
        '''
        Takes a POST request and form object containing data that will be used for
        creating WellReport objects.
        Looks for the following keys in form.cleaned_data:
        wells - a list of choices from MultipleModelChoice form field
        units - a list of choices from a MultipleModelChoice form field
        start_date - an entry from a DateTimeField form field
        end_date - an entry from a DateTimeField form field
        '''
        dt_format = "%x" # Set datetime format here
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
                # Alert the user
                if not matched_readings:
                    messages.info(
                        request,
                        '{}, {} : No readings were matched between {} and {}.'.format(
                            well,
                            unit,
                            start_date.strftime(dt_format),
                            end_date.strftime(dt_format),
                        )
                    )

                # Prepare date for MatPlot and NumPy
                values = []
                dates = []
                mr_count = matched_readings.count() - 1
                try:
                    first_date = matched_readings.earliest('date').date
                except:
                    pass
                try:
                    last_date = matched_readings.latest('date').date
                except:
                    pass
                for reading in matched_readings:
                    values.append(reading.value)
                    dates.append(reading.date.strftime(dt_format))
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
                    first = values[0]
                    last = values[-1]
                    total_readings = len(values)
                    # Create a WellReport model instance for each file
                    report_title='{} {} in {}'.format(
                        w,
                        u.measurement_type.title(),
                        u.name,
                        first_date.strftime(dt_format),
                        last_date.strftime(dt_format)
                    )
                    report, created = self.objects.get_or_create(
                        well=w,
                        user=request.user,
                        title=report_title + ' from {} to {}'.format(
                            first_date.strftime(dt_format),
                            last_date.strftime(dt_format)
                        ),
                        start_date=start_date,
                        end_date=end_date,
                        unit=u,
                        mean=mean,
                        minimum=minimum,
                        maximum=maximum,
                        first=first,
                        first_date=first_date,
                        last=last,
                        last_date=last_date,
                        total_readings=total_readings,
                    )
                    # Create the graph
                    # Create the path where the graph will live
                    dti = pd.DatetimeIndex(dates)
                    df = pd.Series(values, index=dti)
                    print(dti.freq)
    
                    dest_dir = os.path.join(
                        settings.BASE_DIR,
                        datetime.now().strftime("media/%Y/%m/%d/")
                    )
                    try:
                        os.makedirs(dest_dir)
                    except:
                        pass
    
                    dest_path = dest_dir+str(report.pk)+".png"
    
                    plt = self.make_double_sma_time_fig(
                        self, 
                        df, 
                        u.name, 
                        20, 
                        60, 
                        report_title, 
                        total_readings
                    )
                    plt.savefig(dest_path)
                    plt.close()
    
                    if report:
                        report.graph = datetime.now().strftime(
                            "media/%Y/%m/%d/"
                        )+str(report.pk)+".png"
                        report.save()
                else:
                    print('There was no data for {}'.format(w))

class MetaReport(models.Model):
    title = models.CharField(max_length=256, default='untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    csv = models.FileField(upload_to='reports/%Y/%m/%d/', default=None)
    
    def __str__(self):
        return '{} - {}'.format(
            self.start_date.strftime("%x"), 
            self.end_date.strftime("%x"),
        )

    def export_csv(self, request, form):
        '''
        Takes a POST request and form object containing data that will be used for
        creating a MetaReport containing a CSV file.
        Looks for the following keys in form.cleaned_data:
        units - a list of choices from a MultipleModelChoice form field
        start_date - an entry from a DateTimeField form field
        end_date - an entry from a DateTimeField form field
        '''
        # Get the wells specified in the form data
        wells = Well.objects.all()
        units = form.cleaned_data['units']
        # Set model parameters here
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        dt_format = "%x"
        report_context="All data"
        report_title=report_context + " from {} to {}".format(
                start_date.strftime(dt_format),
                end_date.strftime(dt_format),
        )
        # Create the path where the CSV file will live
        media_dir = datetime.now().strftime("media/%Y/%m/%d/")
        dest_dir = os.path.join(
            settings.BASE_DIR,
            media_dir
        )
        try:
            os.makedirs(dest_dir)
        except:
            print('{} could not be created!'.format(dest_dir))
        filename = report_title.replace(" ", "_").replace("/", ".") + str(datetime.now().time()) + ".csv"
        dest_path = dest_dir + filename
        # Initialize the CSV file and header
        csv_file = open(dest_path, 'w', newline='')
        csv_writer = csv.writer(
            csv_file,
            delimiter=',',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL,
        )
        csv_writer.writerow([
            "Well",
            "Units",
            "Start",
            "End",
            "First Date",
            "First Reading",
            "Last Date",
            "Last Reading",
            "Min",
            "Max",
            "Mean",
        ])
        # Perform the analysis for each well
        for well in wells:
            w = Well.objects.get(name=well)
            for unit in units:
                u = Unit.objects.get(name=unit)
                # Match well readings that match the well and the unit
                # and fall within the date range
                # Each time this loop runs it adds a line to the CSV file
                matched_readings = WellReading.objects.filter(
                    well=w,
                    date__range=(start_date, end_date),
                    unit=u
                )
                # Prepare date for Pandas and NumPy
                values = []
                dates = []
                try:
                    first_date = matched_readings.earliest('date').date
                    last_date = matched_readings.latest('date').date
                except:
                    pass
                for reading in matched_readings:
                    values.append(reading.value)
                    dates.append(reading.date.strftime(dt_format))
                if len(values) == len(dates):
                    pass
                else:
                    print("Warning: Number of values does not match number of dates")
                # Get the statistics
                if values:
                    mean = np.mean(values)
                    minimum = min(values)
                    maximum = max(values)
                    first = values[0]
                    last = values[-1]
                    # Write the line to the CSV file
                    csv_writer.writerow([
                        str(w),
                        str(u),
                        start_date.strftime(dt_format),
                        end_date.strftime(dt_format),
                        first_date.strftime(dt_format),
                        first,
                        last_date.strftime(dt_format),
                        last,
                        minimum,
                        maximum,
                        mean,
                    ])
        # Create a MetaReport
        meta_report, created = self.objects.get_or_create(
            user=request.user,
            title=report_title,
            start_date=start_date,
            end_date=end_date,
            csv= datetime.now().strftime("%Y/%m/%d/") + filename
        )
        csv_file.close()

class WellReading(models.Model):
    origin_file = models.CharField(max_length=256, null=True, default=None)
    well = models.ForeignKey(Well, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    value = models.FloatField(default=None)
    quality_code = models.FloatField(null=True, default=None)
    tag_comments = models.CharField(max_length=256, null=True, default='')

    def __str__(self):
        return "{}, {}, {} {}".format(
            self.well,
            self.date,
            self.value,
            self.unit
        )

    def handle_csv_file(self, request, in_file, name='file'):
        '''
        Handles an uploaded file from a POST request by
        getting or creating the following model objects:
        * Well
        * Unit
        * WellReading
        The objects must be imported from analysis.models
        when calling this function.
        The name of the well is derived from the begining of the filename.
        The units are derived from column D [3] in the header.
        The WellReadings are created based on the datetime and value;
        columns A [0] and D [3]
    
    
        Keyword arguments:
        request -- POST request object
        in_file -- CSV formatted file
        name -- the filename
        '''
        # Get or create a Well object based on the begining of the filename
        well_name=name.strip('.csv').rsplit('_')[0]
        well, created = Well.objects.get_or_create(
            name=well_name,
            location="undisclosed"
        )
        # Convert in memory bytestream in to text
        fo = TextIOWrapper(in_file, encoding=request.encoding)
        # Create models out of the uploaded files
        reader = csv.reader(fo)
        headers = next(reader)
        # Keep track of the line number
        line = 1
        unit_name, metric = self.get_unit_type(self, headers[3])
    
        # Get or create a Unit object based on the value header
        try:
            unit, created = Unit.objects.get_or_create(
                name=unit_name,
                measurement_type=metric
            )
        except:
            unit = None
    
        for row in reader:
            # Increment line number
            line += 1
            # From each row, attempt to extract values to be entered into
            # the WellReading Model
            # If it errors, send a message to the view and set
            # the variable to None
            # Extract date
            try:
                date = ptz('US/Pacific').localize(pd.to_datetime(row[0]))
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
    
    def get_unit_type(self, string):
        '''
        Given a string, ascertain the unit type.
        Returns unit, metric as strings.
        '''
        if "milligram per litre" in string:
            unit = 'mg/L'
            metric = 'chloride content'
        elif 'foot' in string:
            unit = 'feet'
            metric = 'height'
        else:
            unit = string
            metric = ''
        return unit, metric
        
