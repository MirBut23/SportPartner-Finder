from django.urls import path
from . import views

app_name = "requests"

urlpatterns = [
    path("", views.requests_list, name="list"),
    path("create/", views.request_create, name="create"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:request_id>/", views.request_detail, name="detail"),
    path("<int:request_id>/edit/", views.request_update, name="update"),
    path("<int:request_id>/cancel/", views.request_cancel, name="cancel"),
]
