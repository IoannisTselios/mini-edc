import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_lists_studies(client, study):
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code == 200
    assert study.code in resp.content.decode()

@pytest.mark.django_db
def test_study_detail_lists_subjects(client, study, subject):
    url = reverse("core:study_detail", args=[study.code])
    resp = client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode()
    assert subject.subject_id in html

@pytest.mark.django_db
def test_subject_detail_lists_visits(client, study, subject, visit_baseline):
    url = reverse("core:subject_detail", args=[study.code, subject.subject_id])
    resp = client.get(url)
    assert resp.status_code == 200
    assert visit_baseline.name in resp.content.decode()
