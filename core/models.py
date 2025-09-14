from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Study(models.Model):
    """
    A clinical study/trial container.
    """
    name = models.CharField(max_length=200)            # Human-readable name
    code = models.CharField(max_length=32, unique=True)  # Short unique code (e.g., 'INCEPT-ICU-01')
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp when study was created

    def __str__(self):
        return f"{self.code} — {self.name}"


class Subject(models.Model):
    """
    A participant (patient) enrolled in a study.
    """
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="subjects",  # Allows study.subjects.all()
    )
    subject_id = models.CharField(max_length=64)  # Site/Study-specific subject identifier
    enrolled_at = models.DateField()              # Date the subject was enrolled

    class Meta:
        # Prevent duplicate subject IDs within the same study
        unique_together = ("study", "subject_id")
        # Common query pattern: list/sort subjects by ID within a study
        ordering = ["study_id", "subject_id"]

    def __str__(self):
        return f"{self.study.code}:{self.subject_id}"


class Visit(models.Model):
    """
    A scheduled/unscheduled visit for a subject.
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="visits",  # Allows subject.visits.all()
    )
    name = models.CharField(max_length=100)  # e.g., 'Baseline', 'Follow-up', 'Day 7'
    visit_date = models.DateField()          # The date of the visit

    class Meta:
        # Helpful default ordering in UIs and lists
        ordering = ["visit_date", "id"]

    def __str__(self):
        return f"{self.subject} — {self.name} ({self.visit_date})"

class AdverseEvent(models.Model):
    """
    A clinical adverse event linked to a subject.
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="adverse_events",      # subject.adverse_events.all()
    )
    onset = models.DateTimeField()          # when it started
    severity = models.CharField(            # controlled severity scale
        max_length=20,
        choices=[("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
    )
    description = models.TextField()        # free-text details
    related_to_study = models.BooleanField(default=False)  # causality flag

    created_by = models.ForeignKey(         # who recorded it (optional for now)
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)   # audit timestamp

    class Meta:
        ordering = ["-onset", "-id"]        # newest first

    def __str__(self):
        return f"{self.subject} — {self.severity} @ {self.onset:%Y-%m-%d %H:%M}"
    

class CRF(models.Model):
    """
    A form definition for a study (e.g., Baseline CRF).
    """
    study = models.ForeignKey("core.Study", on_delete=models.CASCADE, related_name="crfs")
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("study", "name")
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.study.code} — {self.name}"


class CRFField(models.Model):
    """
    A single question/field on a CRF.
    """
    TEXT = "text"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    CHOICE = "choice"
    FIELD_TYPES = [
        (TEXT, "Text"),
        (INT, "Integer"),
        (FLOAT, "Float"),
        (BOOL, "Boolean"),
        (CHOICE, "Choice"),
    ]

    crf = models.ForeignKey(CRF, on_delete=models.CASCADE, related_name="fields")
    name = models.CharField(max_length=120)                 # human label
    code = models.CharField(max_length=64)                  # machine code, unique per CRF
    field_type = models.CharField(max_length=12, choices=FIELD_TYPES, default=TEXT)
    choices = models.JSONField(blank=True, null=True)       # for CHOICE type: ["A","B","C"]
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("crf", "code")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.crf} :: {self.code}"


class Entry(models.Model):
    """
    A captured value for one CRF field at one visit.
    We store normalized text and validate types on input.
    """
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="entries")
    field = models.ForeignKey(CRFField, on_delete=models.CASCADE, related_name="entries")
    value_text = models.TextField(blank=True, null=True)  # normalized string value
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("visit", "field")     # one value per field per visit
        ordering = ["visit_id", "field_id"]

    def __str__(self):
        return f"{self.visit} :: {self.field.code} = {self.value_text}"