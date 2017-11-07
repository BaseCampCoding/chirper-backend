from django.urls import path
from django.http.response import HttpResponse
from app.views import signup

app_name = 'chirper'

urlpatterns = [
    path('signup/', signup, name='signup'),
]
