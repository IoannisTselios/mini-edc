from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("study/<str:study_code>/", views.study_detail, name="study_detail"),
    path("study/<str:study_code>/subject/<str:subject_id>/", views.subject_detail, name="subject_detail"),
    path("study/<str:study_code>/crf-builder/", views.crf_builder, name="crf_builder"),  # NEW
    path("study/<str:study_code>/crf/<int:crf_id>/field/add", views.crf_field_add, name="crf_field_add"),  # NEW
    path("study/<str:study_code>/subject/<str:subject_id>/ae/new", views.adverse_event_create, name="ae_create"),
    path(
    "study/<str:study_code>/subject/<str:subject_id>/visit/<int:visit_id>/",
    views.visit_entry,
    name="visit_entry",
),
]

