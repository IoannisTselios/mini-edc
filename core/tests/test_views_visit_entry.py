import pytest
from django.urls import reverse
from core.models import Entry, CRFField

@pytest.mark.django_db
def test_visit_entry_get_renders_form(client, study, subject, visit_baseline, crf, crf_fields):
    url = reverse("core:visit_entry", args=[study.code, subject.subject_id, visit_baseline.id])
    resp = client.get(url)
    assert resp.status_code == 200
    # the page includes the visit-entry section wrapper
    assert 'id="visit-entry-section"' in resp.content.decode()

@pytest.mark.django_db
def test_visit_entry_post_htmx_saves_entries(client, study, subject, visit_baseline, crf, crf_fields):
    (f1, f2, f3, f4) = crf_fields
    url = reverse("core:visit_entry", args=[study.code, subject.subject_id, visit_baseline.id]) + f"?crf={crf.id}"

    # Simulate htmx POST (HX-Request header) with valid values
    payload = {
        f1.code: "120",          # INT
        f2.code: "37.5",         # FLOAT
        f3.code: "Stable",       # CHOICE
        f4.code: "on",           # BOOL checkbox
        "csrfmiddlewaretoken": "test",  # not validated by client() by default, but harmless
    }
    resp = client.post(url, payload, HTTP_HX_REQUEST="true")
    assert resp.status_code in (200, 204)  # partial should be returned with 200
    html = resp.content.decode()
    assert 'id="visit-entry-section"' in html  # partial returned
    # Entries saved?
    assert Entry.objects.filter(visit=visit_baseline, field=f1, value_text="120").exists()
    assert Entry.objects.filter(visit=visit_baseline, field=f2, value_text="37.5").exists()
    assert Entry.objects.filter(visit=visit_baseline, field=f3, value_text="Stable").exists()
    assert Entry.objects.filter(visit=visit_baseline, field=f4, value_text="true").exists()

@pytest.mark.django_db
def test_visit_entry_validation_error_htmx(client, study, subject, visit_baseline, crf, crf_fields):
    (f1, f2, f3, f4) = crf_fields
    url = reverse("core:visit_entry", args=[study.code, subject.subject_id, visit_baseline.id]) + f"?crf={crf.id}"

    # Invalid integer
    payload = {f1.code: "abc", "csrfmiddlewaretoken": "test"}
    resp = client.post(url, payload, HTTP_HX_REQUEST="true")
    assert resp.status_code == 400
    html = resp.content.decode()
    assert 'id="visit-entry-section"' in html
    assert "Enter a whole number" in html or "Enter a number" in html
