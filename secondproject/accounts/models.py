from django.contrib.auth.models import User
from django.db import models

class UserRole(models.Model):
    JOB_SEEKER = 'job_seeker'
    RECRUITER = 'recruiter'
    CHOICES = [(JOB_SEEKER, 'Job Seeker'), (RECRUITER, 'Recruiter')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=CHOICES, default=JOB_SEEKER)
    company_name = models.CharField(max_length=200, blank=True)  # recruiters only

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
