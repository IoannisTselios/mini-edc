# core/views.py
from django.shortcuts import render, get_object_or_404
from .models import Study, Subject
from .models import Study, Subject, Visit, AdverseEvent, CRF, CRFField
from .forms import AdverseEventForm, CRFForm, CRFFieldForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.utils.timezone import make_aware
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import (
    Study, Subject, Visit, AdverseEvent,
    CRF, CRFField, Entry
)
from .forms import AdverseEventForm, CRFForm, CRFFieldForm, make_crf_entry_form


def dashboard(request):
    """
    List all studies (top-level view).
    """
    studies = Study.objects.all().order_by("code")
    return render(request, "core/dashboard.html", {"studies": studies})

def study_detail(request, study_code: str):
    """
    Show subjects enrolled in a specific study.
    """
    study = get_object_or_404(Study, code=study_code)
    subjects = study.subjects.all().order_by("subject_id")  # thanks to related_name="subjects"
    return render(request, "core/study_detail.html", {"study": study, "subjects": subjects})

def subject_detail(request, study_code: str, subject_id: str):
    study = get_object_or_404(Study, code=study_code)
    subject = get_object_or_404(Subject, study=study, subject_id=subject_id)
    visits = subject.visits.all().order_by("visit_date", "id")
    aevents = subject.adverse_events.all()  # newest first (Meta.ordering)

    form = AdverseEventForm()  # empty form for the page
    return render(request, "core/subject_detail.html", {
        "study": study,
        "subject": subject,
        "visits": visits,
        "aevents": aevents,
        "ae_form": form,
    })

def _render_ae_partial(request, study, subject):
    """Helper: render the AE section partial with fresh context."""
    aevents = subject.adverse_events.all()  # newest first (Meta.ordering)
    form = AdverseEventForm()
    return render(
        request,
        "core/partials/ae_section.html",
        {"study": study, "subject": subject, "aevents": aevents, "ae_form": form},
    )

@require_POST
def adverse_event_create(request, study_code: str, subject_id: str):
    study = get_object_or_404(Study, code=study_code)
    subject = get_object_or_404(Subject, study=study, subject_id=subject_id)

    form = AdverseEventForm(request.POST)
    if form.is_valid():
        ae = form.save(commit=False)
        ae.subject = subject
        if request.user.is_authenticated:
            ae.created_by = request.user
        # Make onset timezone-aware if it came from a datetime-local input
        if isinstance(ae.onset, datetime) and ae.onset.tzinfo is None:
            ae.onset = make_aware(ae.onset)
        ae.save()

        # If this is an htmx request, return just the updated section
        if request.headers.get("HX-Request") == "true":
            return _render_ae_partial(request, study, subject)

        messages.success(request, "Adverse event recorded.")
        return redirect("core:subject_detail", study_code=study.code, subject_id=subject.subject_id)

    # Invalid form:
    if request.headers.get("HX-Request") == "true":
        # Re-render partial with errors (keeps user in place)
        aevents = subject.adverse_events.all()
        return render(
            request,
            "core/partials/ae_section.html",
            {"study": study, "subject": subject, "aevents": aevents, "ae_form": form},
            status=400,
        )

    # Non-htmx: re-render the full subject page with errors (fallback)
    visits = subject.visits.all().order_by("visit_date", "id")
    aevents = subject.adverse_events.all()
    return render(request, "core/subject_detail.html", {
        "study": study,
        "subject": subject,
        "visits": visits,
        "aevents": aevents,
        "ae_form": form,
    }, status=400)


def crf_builder(request, study_code: str):
    """
    Create CRFs and manage fields for a given study.
    """
    study = get_object_or_404(Study, code=study_code)
    if request.method == "POST":
        form = CRFForm(request.POST)
        if form.is_valid():
            crf = form.save(commit=False)
            crf.study = study
            crf.save()
            messages.success(request, "CRF created.")
            return redirect("core:crf_builder", study_code=study.code)
    else:
        form = CRFForm()

    crfs = study.crfs.prefetch_related("fields")
    return render(request, "core/crf_builder.html", {"study": study, "form": form, "crfs": crfs})


@require_POST
def crf_field_add(request, study_code: str, crf_id: int):
    """
    Add a field to a specific CRF.
    """
    study = get_object_or_404(Study, code=study_code)
    crf = get_object_or_404(CRF, id=crf_id, study=study)
    form = CRFFieldForm(request.POST)
    if form.is_valid():
        field = form.save(commit=False)
        field.crf = crf
        field.save()
        messages.success(request, f"Field '{field.code}' added to CRF '{crf.name}'.")
        return redirect("core:crf_builder", study_code=study.code)
    messages.error(request, "Invalid field data.")
    return redirect("core:crf_builder", study_code=study.code)

def _render_visit_entry_partial(request, study, subject, visit, selected_crf, form, entries, status=200):
    """Return just the visit-entry section (htmx target)."""
    return render(
        request,
        "core/partials/visit_entry_section.html",
        {
            "study": study,
            "subject": subject,
            "visit": visit,
            "selected_crf": selected_crf,
            "form": form,
            "entries": entries,
        },
        status=status,
    )

def visit_entry(request, study_code: str, subject_id: str, visit_id: int):
    study = get_object_or_404(Study, code=study_code)
    subject = get_object_or_404(Subject, study=study, subject_id=subject_id)
    visit = get_object_or_404(Visit, id=visit_id, subject=subject)

    crfs = list(study.crfs.filter(is_active=True).prefetch_related("fields").order_by("name", "id"))
    if not crfs:
        # No CRFs; render full page with message
        return render(request, "core/visit_entry.html", {
            "study": study, "subject": subject, "visit": visit,
            "crfs": [], "selected_crf": None, "form": None, "entries": [],
        })

    # Pick CRF from querystring or default to first
    try:
        crf_id = int(request.GET.get("crf")) if request.GET.get("crf") else None
    except (TypeError, ValueError):
        crf_id = None
    selected_crf = next((c for c in crfs if c.id == crf_id), None) if crf_id else crfs[0]

    # Prefill from existing entries
    entries_qs = Entry.objects.filter(visit=visit, field__crf=selected_crf).select_related("field")
    initial = {e.field.code: e.value_text for e in entries_qs}

    is_htmx = bool(request.headers.get("HX-Request"))

    if request.method == "POST":
        form = make_crf_entry_form(selected_crf, post_data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                for field in selected_crf.fields.all().order_by("order", "id"):
                    raw = form.cleaned_data.get(field.code, None)
                    if raw is None or raw == "":
                        norm = None
                    elif field.field_type == CRFField.BOOL:
                        norm = "true" if raw else "false"
                    else:
                        norm = str(raw)

                    Entry.objects.update_or_create(
                        visit=visit, field=field, defaults={"value_text": norm}
                    )
            # After saving, rebuild fresh form (prefilled with new values)
            entries_qs = Entry.objects.filter(visit=visit, field__crf=selected_crf).select_related("field").order_by("field__order","field__id")
            form = make_crf_entry_form(selected_crf, initial_data={e.field.code: e.value_text for e in entries_qs})

            if is_htmx:
                # Return only the section (no full-page reload)
                return _render_visit_entry_partial(request, study, subject, visit, selected_crf, form, entries_qs)

            messages.success(request, f"Saved data for CRF '{selected_crf.name}'.")
            # Full page fallback
            return redirect(f"{request.path}?crf={selected_crf.id}")

        # Invalid form
        if is_htmx:
            # Keep current entries for display
            entries_qs = entries_qs.order_by("field__order","field__id")
            return _render_visit_entry_partial(request, study, subject, visit, selected_crf, form, entries_qs, status=400)

        entries_qs = entries_qs.order_by("field__order","field__id")
        return render(request, "core/visit_entry.html", {
            "study": study, "subject": subject, "visit": visit,
            "crfs": crfs, "selected_crf": selected_crf, "form": form, "entries": entries_qs,
        }, status=400)

    # GET: initial render
    form = make_crf_entry_form(selected_crf, initial_data=initial)
    entries_qs = entries_qs.order_by("field__order","field__id")

    if is_htmx:
        # htmx CRF switch (hx-get) → return only section
        return _render_visit_entry_partial(request, study, subject, visit, selected_crf, form, entries_qs)

    # Full page render
    return render(request, "core/visit_entry.html", {
        "study": study, "subject": subject, "visit": visit,
        "crfs": crfs, "selected_crf": selected_crf, "form": form, "entries": entries_qs,
    })