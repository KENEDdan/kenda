from django import forms
from .models import Student, Grade, Stream, AcademicYear


class StudentEnrolForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name',
            'gender', 'date_of_birth', 'photo',
            'grade', 'stream', 'academic_year',
            'phone', 'email', 'address', 'nationality',
            'guardian_name', 'guardian_phone',
            'guardian_email', 'guardian_relationship',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style every field
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control kenda-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select kenda-input'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control kenda-input'
            else:
                field.widget.attrs['class'] = 'form-control kenda-input'
            field.widget.attrs['placeholder'] = field.label or ''
        # Default academic year to current
        try:
            current_year = AcademicYear.objects.get(is_current=True)
            self.fields['academic_year'].initial = current_year
        except AcademicYear.DoesNotExist:
            pass