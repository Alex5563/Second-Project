from django.contrib.auth.models import User
from django.db import models


class Job(models.Model):
    REMOTE = 'remote'
    ONSITE = 'onsite'
    WORKPLACE_CHOICES = [
        (REMOTE, 'Remote'),
        (ONSITE, 'On-site'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    skills = models.ManyToManyField('profiles.Skill', blank=True)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    salary_min = models.PositiveIntegerField()
    salary_max = models.PositiveIntegerField()
    workplace = models.CharField(max_length=20, choices=WORKPLACE_CHOICES)
    visa_sponsorship = models.BooleanField(default=False)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Application(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Job,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.job.title
