import pytest
from django.urls import reverse
from django.utils import timezone

@pytest.mark.django_db
def test_adverse_event_create_htmx(client, study, subject):
    url = reverse("core:ae_create", args=[study.code, subject.subject_id])

    payload = {
        "onset": timezone.now().strftime("%Y-%m-%dT%H:%M"),  # HTML datetime-local format
        "severity": "moderate",
        "description": "Fever and cough",
        "related_to_study": "on",
    }
    resp = client.post(url, payload, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    html = resp.content.decode()
    # partial wrapper should be present
    assert 'id="ae-section"' in html
    # description should appear in the table
    assert "Fever and cough" in html

@pytest.mark.django_db
def test_adverse_event_invalid_htmx(client, study, subject):
    url = reverse("core:ae_create", args=[study.code, subject.subject_id])
    # Missing required onset → should return partial with 400
    payload = {
        "severity": "mild",
        "description": "Note without onset",
    }
    resp = client.post(url, payload, HTTP_HX_REQUEST="true")
    assert resp.status_code == 400
    html = resp.content.decode()
    assert 'id="ae-section"' in html
    # look for a generic error marker
    assert "errorlist" in html or "This field is required" in html
