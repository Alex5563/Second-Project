from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'company',
            'description',
            'skills',
            'location',
            'salary_min',
            'salary_max',
            'workplace',
            'visa_sponsorship',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['description'].required = True

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(
                field.widget,
                (forms.Select, forms.SelectMultiple),
            ):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()

        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            self.add_error(
                'salary_max',
                'Maximum salary must be at least the minimum salary.',
            )

        return cleaned_data