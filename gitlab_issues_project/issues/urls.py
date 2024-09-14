from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_board, name='issue_board'),
]