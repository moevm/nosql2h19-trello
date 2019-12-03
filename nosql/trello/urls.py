from django.urls import path
from .views import *

urlpatterns = [
    path('', KeyGet.as_view(), name='start_page_url'),
    path('next', Next.as_view(), name='next_page_url'),
    path('boards', BoardGet.as_view(), name='boards_page_url'),
    path('settings', SettingsGet.as_view(), name='settings_page_url'),
    path('download', Download.as_view(), name='download_page_url'),
    path('import', Import.as_view(), name='import_page_url'),
    path('export', Export.as_view(), name='export_page_url'),
]
