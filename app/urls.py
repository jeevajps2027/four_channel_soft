from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from .views import measurement,master,parameter,report,comport,data,login,measure_data,delete_measure_data,measurement_count,spc


urlpatterns = [
     path('',login,name="login"),
    path('measurement/',measurement,name="measurement"),
    path('master/',master,name="master"),
    path('parameter/',parameter,name="parameter"),
    path('report/',report,name="report"),
    path('data/',data,name="data"),
    path('comport/',comport,name="comport"),
    path('measure_data/',measure_data,name="measure_data"),
    path('delete_measure_data/',delete_measure_data,name="delete_measure_data"),
    path('measurement_count/',measurement_count,name="measurement_count"),
    path('spc/',spc,name="spc"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)