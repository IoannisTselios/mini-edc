import pytest

@pytest.mark.django_db
def test_models_import():
    # Import your app and a model to ensure Django loads
    from core.models import Study
    assert Study._meta.app_label == "core"

def test_reverse_dashboard():
    # Ensure your URL names are wired correctly
    from django.urls import reverse
    url = reverse("core:dashboard")
    assert url == "/"
