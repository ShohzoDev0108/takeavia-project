from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("turlar/", views.tour_list, name="tour_list"),
    path("tur/<int:pk>/", views.tour_detail, name="tour_detail"),
    path("qidiruv/", views.flight_search, name="flight_search"),
    path("sorov/", views.leave_request, name="leave_request"),
]
