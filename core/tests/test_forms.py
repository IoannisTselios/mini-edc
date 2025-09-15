import pytest
from core.forms import CRFFieldForm
from core.models import CRF, Study

@pytest.mark.django_db
def test_crffieldform_choices_accepts_json():
    study = Study.objects.create(code="S1", name="Study 1")
    crf = CRF.objects.create(study=study, name="CRF", is_active=True)

    form = CRFFieldForm(data={
        "crf": crf.id,
        "name": "Clinical Status",
        "code": "status",
        "field_type": "choice",
        "choices": '["Stable","Critical"]',  # JSON string
        "required": True,
        "order": 1,
    })
    assert form.is_valid(), form.errors
    obj = form.save(commit=False)
    assert obj.choices == ["Stable", "Critical"]

@pytest.mark.django_db
def test_crffieldform_choices_rejects_bad_string():
    study = Study.objects.create(code="S2", name="Study 2")
    crf = CRF.objects.create(study=study, name="CRF", is_active=True)

    form = CRFFieldForm(data={
        "crf": crf.id,
        "name": "Bad Choices",
        "code": "bad",
        "field_type": "choice",
        "choices": 'Never',  # invalid
        "required": False,
        "order": 2,
    })
    assert not form.is_valid()
    assert "choices" in form.errors
