from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=200)
    degree = models.CharField(max_length=100, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)

    def clean(self):
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValidationError('End year cannot be before start year.')

class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')

class ProfileLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=50)
    url = models.URLField()
from django.contrib.auth.models import User
from django.db import models

class PrivacySettings(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='privacy')
    visible_to_recruiters = models.BooleanField('Let recruiters view my profile', default=True)
    show_email = models.BooleanField('Show my email address', default=False)
    show_skills = models.BooleanField('Show my skills', default=True)
    show_education = models.BooleanField('Show my education', default=True)
    show_experience = models.BooleanField('Show my work experience', default=True)
    show_links = models.BooleanField('Show my links', default=True)

    def __str__(self):
        return f'Privacy settings for {self.profile.user.username}'