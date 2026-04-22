from django import forms
from .models import Teacher, Department


class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher
        fields = [
            'first_name', 'middle_name', 'last_name',
            'gender', 'date_of_birth', 'photo',
            'nationality', 'phone', 'email', 'address',
            'department', 'employment_type', 'qualification',
            'specialization', 'emergency_contact_name',
            'emergency_contact_phone',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs['class'] = 'form-control kenda-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select kenda-input'
            elif isinstance(widget, forms.FileInput):
                widget.attrs['class'] = 'form-control kenda-input'
            else:
                widget.attrs['class'] = 'form-control kenda-input'
            field.widget.attrs['placeholder'] = field.label or ''