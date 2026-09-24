from django import forms
from .models import Profile, Skill, Education, WorkExperience, ProfileLink, PrivacySettings

class ProfileForm(forms.ModelForm):
    skills_text = forms.CharField(
        label='Skills', required=False,
        help_text='Comma-separated, e.g. Python, Django, SQL')

    class Meta:
        model = Profile
        fields = ['headline', 'summary']
        widgets = {'summary': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['headline'].required = True
        if self.instance.pk:
            self.fields['skills_text'].initial = ', '.join(
                self.instance.skills.values_list('name', flat=True))
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_skills_text(self):
        names, seen = [], set()
        for part in self.cleaned_data['skills_text'].split(','):
            name = part.strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                names.append(name)
        return names

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            skills = []
            for name in self.cleaned_data['skills_text']:
                skill = Skill.objects.filter(name__iexact=name).first()
                skills.append(skill or Skill.objects.create(name=name))
            profile.skills.set(skills)
        return profile

EducationFormSet = forms.inlineformset_factory(
    Profile, Education,
    fields=['school', 'degree', 'field_of_study', 'start_year', 'end_year'],
    extra=1, can_delete=True)

ExperienceFormSet = forms.inlineformset_factory(
    Profile, WorkExperience,
    fields=['company', 'title', 'start_date', 'end_date', 'description'],
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
        'description': forms.Textarea(attrs={'rows': 2}),
    },
    extra=1, can_delete=True)

LinkFormSet = forms.inlineformset_factory(
    Profile, ProfileLink, fields=['label', 'url'], extra=1, can_delete=True)
class PrivacyForm(forms.ModelForm):
    class Meta:
        model = PrivacySettings
        fields = ['visible_to_recruiters', 'show_email', 'show_skills',
                  'show_education', 'show_experience', 'show_links']

    def __init__(self, *args, **kwargs):
        super(PrivacyForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-check-input'})