from django.urls import path
from django.http.response import HttpResponse
from app.views import signup, feed, login, logout, username_exists, chirp

app_name = 'chirper'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('chirp/', chirp, name='chirp'),
    path(
        'username_exists/<username>/', username_exists, name='username_exists'),
    path('<username>/', feed, name='feed'),
]
