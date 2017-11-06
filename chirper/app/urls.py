from django.urls import path
from django.http.response import HttpResponse

app_name = 'chirper'

urlpatterns = [
    path('', lambda request: HttpResponse("Hello World")),
    path('goodbye/', lambda r: HttpResponse("Good Bye"))
]
