from django.urls import path
from . import views

app_name = "requests"

urlpatterns = [
    path("", views.requests_list, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:request_id>/", views.request_detail, name="detail"),
]
