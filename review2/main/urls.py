from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path("", views.index, name="index"),
    path("train/", views.train, name="train"),
    path("similar/", views.get_similar, name="similar"),
    path("task_status/<task_id>/", views.task_status, name="task_status"),
]
