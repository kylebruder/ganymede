from django.contrib import admin
from .models import Well, WellReading, WellReport, Unit, MetaReport
# Register your models here.

admin.site.register(Well)
admin.site.register(WellReading)
admin.site.register(WellReport)
admin.site.register(Unit)
admin.site.register(MetaReport)
