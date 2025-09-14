import json
from django import forms
from .models import CRF, AdverseEvent, CRFField, Entry

class AdverseEventForm(forms.ModelForm):
    class Meta:
        model = AdverseEvent
        fields = ["onset", "severity", "description", "related_to_study"]
        widgets = {
            # HTML5 datetime-local for easy input
            "onset": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

class CRFForm(forms.ModelForm):
    class Meta:
        model = CRF
        fields = ["name", "is_active"]

class CRFFieldForm(forms.ModelForm):
    class Meta:
        model = CRFField
        fields = ["name", "code", "field_type", "choices", "required", "order"]
        widgets = {
            "choices": forms.Textarea(attrs={"rows": 2, "placeholder": 'For CHOICE: ["A","B"]'}),
        }

    def clean_choices(self):
        """
        Allow empty, a JSON array string, or a real list.
        Convert valid JSON to a Python list. Reject bad input for CHOICE fields.
        """
        val = self.cleaned_data.get("choices")

        # If blank, store as None
        if val in ("", None):
            return None

        # If already a list (e.g., posted back by admin), accept as-is
        if isinstance(val, list):
            return val

        # If a string, try to parse JSON into a list
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
            except Exception:
                raise forms.ValidationError("Choices must be valid JSON, e.g. [\"A\", \"B\"].")

            if not isinstance(parsed, list):
                raise forms.ValidationError("Choices must be a JSON array, e.g. [\"A\", \"B\"].")

            # Coerce all items to strings for uniformity
            return [str(x) for x in parsed]

        # Any other type is invalid
        raise forms.ValidationError("Invalid choices format. Use a JSON array, e.g. [\"A\", \"B\"].")

def _form_field_for_crf_field(f: CRFField):
    if f.field_type == CRFField.TEXT:
        return forms.CharField(label=f.name, required=f.required)
    if f.field_type == CRFField.INT:
        return forms.IntegerField(label=f.name, required=f.required)
    if f.field_type == CRFField.FLOAT:
        return forms.FloatField(label=f.name, required=f.required)
    if f.field_type == CRFField.BOOL:
        # Use Checkbox for bool; unchecked = False (when not required)
        return forms.BooleanField(label=f.name, required=False)
    if f.field_type == CRFField.CHOICE:
        choices = []
        if f.choices:
            try:
                # choices is a JSON list like ["A","B"]
                for c in f.choices:
                    choices.append((str(c), str(c)))
            except Exception:
                pass
        return forms.ChoiceField(label=f.name, required=f.required, choices=choices)
    # Fallback
    return forms.CharField(label=f.name, required=f.required)

def make_crf_entry_form(crf: CRF, initial_data=None, post_data=None):
    """
    Build a dynamic form class with one field per CRFField (ordered).
    initial_data: dict of {field_code: value} to prefill from existing entries.
    post_data: request.POST if submitting.
    """
    fields = crf.fields.all().order_by("order", "id")

    # Build form subclass on the fly
    class _CRFEntryForm(forms.Form):
        pass

    for f in fields:
        form_field = _form_field_for_crf_field(f)
        # Pre-fill initial values (strings) if provided
        if initial_data and f.code in initial_data:
            form_field.initial = initial_data[f.code]
        _CRFEntryForm.base_fields[f.code] = form_field

    return _CRFEntryForm(post_data) if post_data is not None else _CRFEntryForm()