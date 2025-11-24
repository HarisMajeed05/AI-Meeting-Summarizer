from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("export_pdf/", views.export_pdf, name="export_pdf"),
    path("record/", views.record_audio, name="record_audio"),  # live recording API
]
