from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserRole
from profiles.models import Profile, Skill

from .models import Job


class JobsIndexTests(TestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user('recruiter', password='pass')
        UserRole.objects.create(user=self.recruiter, role=UserRole.RECRUITER, company_name='Acme')

        self.seeker = User.objects.create_user('seeker', password='pass')
        UserRole.objects.create(user=self.seeker, role=UserRole.JOB_SEEKER)
        self.profile = Profile.objects.create(user=self.seeker)

        self.python = Skill.objects.create(name='Python')
        self.django = Skill.objects.create(name='Django')
        self.java = Skill.objects.create(name='Java')

        self.job_both = Job.objects.create(
            title='Full Stack Python',
            company='Acme',
            location='Atlanta',
            salary_min=90000,
            salary_max=120000,
            workplace=Job.REMOTE,
            visa_sponsorship=True,
            posted_by=self.recruiter,
        )
        self.job_both.skills.set([self.python, self.django])

        self.job_python = Job.objects.create(
            title='Python Developer',
            company='Beta',
            location='Remote',
            salary_min=80000,
            salary_max=100000,
            workplace=Job.REMOTE,
            visa_sponsorship=False,
            posted_by=self.recruiter,
        )
        self.job_python.skills.set([self.python])

        self.job_java = Job.objects.create(
            title='Java Engineer',
            company='Gamma',
            location='New York',
            salary_min=95000,
            salary_max=130000,
            workplace=Job.ONSITE,
            visa_sponsorship=True,
            posted_by=self.recruiter,
        )
        self.job_java.skills.set([self.java])

        self.url = reverse('jobs.index')

    def test_recommendations_rank_by_skill_overlap(self):
        self.profile.skills.set([self.python, self.django])
        self.client.login(username='seeker', password='pass')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        recommended = list(response.context['template_data']['recommended'])
        self.assertEqual(recommended[0], self.job_both)
        self.assertEqual(recommended[1], self.job_python)
        self.assertNotIn(self.job_java, recommended)
        self.assertContains(response, '2 of your skills')
        self.assertContains(response, '1 of your skills')

    def test_no_skills_shows_message_not_recommendations(self):
        self.client.login(username='seeker', password='pass')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['template_data']['has_skills'])
        self.assertEqual(list(response.context['template_data']['recommended']), [])
        self.assertContains(response, 'Add skills to your profile')
        self.assertContains(response, reverse('profiles.edit'))

    def test_title_filter(self):
        self.client.login(username='seeker', password='pass')
        response = self.client.get(self.url, {'title': 'Java'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertEqual(jobs, [self.job_java])
        self.assertTrue(response.context['template_data']['has_filters'])

    def test_location_filter(self):
        self.client.login(username='seeker', password='pass')
        response = self.client.get(self.url, {'location': 'Atlanta'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertEqual(jobs, [self.job_both])

    def test_workplace_filter(self):
        self.client.login(username='seeker', password='pass')
        response = self.client.get(self.url, {'workplace': 'onsite'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertEqual(jobs, [self.job_java])

    def test_visa_filter(self):
        self.client.login(username='seeker', password='pass')
        response = self.client.get(self.url, {'visa': 'no'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertEqual(jobs, [self.job_python])

    def test_skills_filter_requires_every_named_skill(self):
        self.client.login(username='seeker', password='pass')
        response = self.client.get(self.url, {'skills': 'Python, Django'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertEqual(jobs, [self.job_both])

    def test_salary_filters(self):
        self.client.login(username='seeker', password='pass')

        response = self.client.get(self.url, {'salary_min': '80000'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertIn(self.job_both, jobs)

        response = self.client.get(self.url, {'salary_max': '70000'})
        jobs = list(response.context['template_data']['jobs'])
        self.assertNotIn(self.job_both, jobs)

    def test_recruiter_redirected_home(self):
        self.client.login(username='recruiter', password='pass')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home.index'))
