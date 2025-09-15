import pytest
from datetime import date, timedelta
from django.utils import timezone

from core.models import Study, Subject, Visit, CRF, CRFField, Entry

@pytest.fixture
def study(db):
    return Study.objects.create(code="INCEPT-ICU-TEST", name="INCEPT ICU Test Study")

@pytest.fixture
def subject(db, study):
    return Subject.objects.create(study=study, subject_id="001", enrolled_at=date.today())

@pytest.fixture
def visit_baseline(db, subject):
    return Visit.objects.create(subject=subject, name="Baseline", visit_date=date.today())

@pytest.fixture
def visit_day7(db, subject):
    return Visit.objects.create(subject=subject, name="Day 7", visit_date=date.today() + timedelta(days=7))

@pytest.fixture
def crf(db, study):
    return CRF.objects.create(study=study, name="Baseline CRF", is_active=True)

@pytest.fixture
def crf_fields(db, crf):
    # Order matters for rendering
    f1 = CRFField.objects.create(crf=crf, order=1, code="bp_sys", name="Systolic BP", field_type=CRFField.INT, required=True)
    f2 = CRFField.objects.create(crf=crf, order=2, code="temp_c", name="Temperature (°C)", field_type=CRFField.FLOAT, required=False)
    f3 = CRFField.objects.create(crf=crf, order=3, code="status", name="Clinical Status", field_type=CRFField.CHOICE, choices=["Stable", "Critical"])
    f4 = CRFField.objects.create(crf=crf, order=4, code="on_vent", name="On Ventilation", field_type=CRFField.BOOL)
    return (f1, f2, f3, f4)

@pytest.fixture
def add_entries(db):
    # Helper to populate entries for a visit
    def _add(visit, field_values):
        for field, value in field_values.items():
            Entry.objects.update_or_create(visit=visit, field=field, defaults={"value_text": value})
    return _add
