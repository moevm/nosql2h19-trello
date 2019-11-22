from django.urls import path
from .views import *

urlpatterns = [
    path('', LinkGet.as_view(), name='start_page_url'),
    path('settings', SettingsGet.as_view(), name='settings_page_url'),
]
