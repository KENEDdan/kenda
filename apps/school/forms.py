from django import forms
from .models import SchoolProfile


class SchoolProfileForm(forms.ModelForm):

    class Meta:
        model = SchoolProfile
        fields = [
            'name', 'short_name', 'motto', 'registration_number',
            'school_type', 'logo',
            'primary_color', 'secondary_color',
            'email', 'phone', 'phone_alt', 'website',
            'address', 'city', 'country', 'po_box',
            'school_week_start', 'school_week_end',
            'id_card_footer', 'id_card_valid_years',
            'principal_name', 'principal_signature',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure color fields always have a default value
        if not self.instance.primary_color:
            self.fields['primary_color'].initial = '#2D1B69'
        if not self.instance.secondary_color:
            self.fields['secondary_color'].initial = '#F59E0B'

        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs['class'] = 'form-control kenda-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select kenda-input'
            elif isinstance(widget, forms.FileInput):
                widget.attrs['class'] = 'form-control kenda-input'
            elif isinstance(widget, forms.TextInput) and \
                    widget.attrs.get('type') == 'color':
                widget.attrs['class'] = 'kenda-color-input'
            else:
                widget.attrs['class'] = 'form-control kenda-input'