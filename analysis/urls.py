from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns

app_name = "analysis"
#try:
urlpatterns = [
    path('upload/', views.FileFieldView.as_view(), name='upload'),
    path(
        'create-meta-report/', 
         views.CreateMetaReport.as_view(),
         name='create_meta_report'
    ),
    path(
        'meta-reports/',
         views.MetaReportListView.as_view(),
         name='metareport_list'
    ),
    path(
        'meta-reports/<int:pk>/',
        views.MetaReportDetailView.as_view(),
        name='meta_report_detail'
    ),
    path(
        'create-report/',
        views.CreateWellReport.as_view(),
        name='create_report'
    ),
    path(
        'enter-well-data/',
        views.CreateWellReading.as_view(),
        name='enter_well_data'
    ),
    path(
        'reports/',
        views.WellReportListView.as_view(),
        name='report_list'
    ),
    path(
        'reports/<int:pk>/',
        views.WellReportDetailView.as_view(),
        name='report_detail'
    )
]
#except:
#    urlpatterns = []

