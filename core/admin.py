from django.contrib import admin
from .models import Study, Subject, Visit, AdverseEvent, CRF, CRFField, Entry


# --- Inline so you can add/edit Visits directly on a Subject page ---
class VisitInline(admin.TabularInline):
    model = Visit
    extra = 1                      # show one empty row by default
    fields = ("name", "visit_date")
    ordering = ("visit_date",)


# --- Study admin: top-level container ---
@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "created_at")   # columns in list view
    search_fields = ("code", "name")                # top-right search
    ordering = ("code",)                            # default sort
    # readonly_fields = ("created_at",)             # uncomment to lock field in form
    # inlines: we don't inline Subject here; Subjects can be numerous


# --- Subject admin: patient within a study ---
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_id", "study", "enrolled_at")
    list_filter = ("study",)                        # left sidebar filter
    search_fields = ("subject_id", "study__code")   # search by subject or study code
    ordering = ("study__code", "subject_id")
    inlines = [VisitInline]                         # add/edit visits on the same page

    # Make it a bit nicer to pick the study when lots exist
    autocomplete_fields = ("study",)                # requires StudyAdmin.search_fields


# --- Visit admin: timepoint for a subject ---
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "visit_date")
    list_filter = ("subject__study", "visit_date")  # filter by study and date
    search_fields = ("subject__subject_id", "subject__study__code", "name")
    ordering = ("visit_date", "id")
    autocomplete_fields = ("subject",)              # helpful if many subjects exist


@admin.register(AdverseEvent)
class AdverseEventAdmin(admin.ModelAdmin):
    list_display = ("subject", "onset", "severity", "related_to_study", "created_at", "created_by")
    list_filter = ("severity", "related_to_study", "subject__study", "onset")
    search_fields = ("subject__subject_id", "subject__study__code", "description")
    ordering = ("-onset",)
    autocomplete_fields = ("subject",)

class CRFFieldInline(admin.TabularInline):
    model = CRFField
    extra = 1
    fields = ("order", "code", "name", "field_type", "required", "choices")
    ordering = ("order", "id")


@admin.register(CRF)
class CRFAdmin(admin.ModelAdmin):
    list_display = ("study", "name", "is_active")
    list_filter = ("study", "is_active")
    search_fields = ("name", "study__code")
    ordering = ("study__code", "name")
    inlines = [CRFFieldInline]


@admin.register(CRFField)
class CRFFieldAdmin(admin.ModelAdmin):
    list_display = ("crf", "order", "code", "name", "field_type", "required")
    list_filter = ("field_type", "required", "crf__study")
    search_fields = ("code", "name", "crf__name", "crf__study__code")
    ordering = ("crf__study__code", "crf__name", "order")


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("visit", "field", "value_text", "updated_at")
    list_filter = ("field__crf__study", "field__crf", "visit__subject", "updated_at")
    search_fields = ("field__code", "visit__subject__subject_id", "value_text")
    ordering = ("-updated_at",)
    autocomplete_fields = ("visit", "field")