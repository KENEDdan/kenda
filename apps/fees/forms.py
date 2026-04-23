from django import forms
from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment
from apps.students.models import Student, Grade, AcademicYear
from apps.academics.models import Term
import datetime


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control kenda-input'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control kenda-input'


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['category', 'grade', 'academic_year', 'term', 'amount', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select kenda-input'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control kenda-input'


class InvoiceCreateForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(status='active').order_by('last_name'),
        widget=forms.Select(attrs={'class': 'form-select kenda-input'})
    )
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select kenda-input'})
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select kenda-input'})
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control kenda-input'}
        )
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control kenda-input'})
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'payment_date', 'reference', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_date'].initial = datetime.date.today()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select kenda-input'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control kenda-input'
            else:
                field.widget.attrs['class'] = 'form-control kenda-input'