from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from .views import measurement,master,parameter,report,gen_setting


urlpatterns = [
    path('',measurement,name="measurement"),
    path('master/',master,name="master"),
    path('parameter/',parameter,name="parameter"),
    path('report/',report,name="report"),
    path('settings/',gen_setting,name="gen_setting"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)