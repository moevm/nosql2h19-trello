from django.urls import path
from trello.views import TestView

urlpatterns = [
    path('', TestView.as_view()),
]
