import pytest
from core.models import Study, Subject, Visit

@pytest.mark.django_db
def test_models_str_and_relations(study, subject, visit_baseline):
    assert str(study) == f"{study.code} — {study.name}"
    assert str(subject).startswith(f"{study.code}:{subject.subject_id}")
    assert str(visit_baseline).startswith(str(subject))

    # reverse relations exist
    assert list(study.subjects.all()) == [subject]
    assert list(subject.visits.all()) == [visit_baseline]

@pytest.mark.django_db
def test_subject_unique_within_study(study):
    Subject.objects.create(study=study, subject_id="001", enrolled_at=study.created_at.date())
    with pytest.raises(Exception):
        # same subject_id in same study should violate unique_together
        Subject.objects.create(study=study, subject_id="001", enrolled_at=study.created_at.date())
