from django.urls import path
from django.http.response import HttpResponse
from app.views import signup, feed

app_name = 'chirper'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('<username>/', feed, name='feed'),
]
