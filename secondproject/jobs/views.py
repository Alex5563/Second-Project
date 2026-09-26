from django.db.models import Count, Q
from django.shortcuts import render
from accounts.permissions import job_seeker_required
from profiles.models import Profile
from .models import Job


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@job_seeker_required
def index(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    profile_skill_ids = set(profile.skills.values_list('id', flat=True))
    skill_ids = list(profile_skill_ids)

    title = request.GET.get('title', '').strip()
    skills_param = request.GET.get('skills', '').strip()
    location = request.GET.get('location', '').strip()
    salary_min_param = request.GET.get('salary_min', '').strip()
    salary_max_param = request.GET.get('salary_max', '').strip()
    workplace = request.GET.get('workplace', '').strip()
    visa = request.GET.get('visa', '').strip()

    has_filters = any([
        title,
        skills_param,
        location,
        salary_min_param,
        salary_max_param,
        workplace in (Job.REMOTE, Job.ONSITE),
        visa in ('yes', 'no'),
    ])

    recommended = []
    jobs = Job.objects.prefetch_related('skills').order_by('-created_at')

    if has_filters:
        if title:
            jobs = jobs.filter(title__icontains=title)
        if skills_param:
            for name in [s.strip() for s in skills_param.split(',') if s.strip()]:
                jobs = jobs.filter(skills__name__iexact=name)
        if location:
            jobs = jobs.filter(location__icontains=location)
        seeker_min = _parse_int(salary_min_param) if salary_min_param else None
        seeker_max = _parse_int(salary_max_param) if salary_max_param else None
        if seeker_min is not None:
            jobs = jobs.filter(salary_max__gte=seeker_min)
        if seeker_max is not None:
            jobs = jobs.filter(salary_min__lte=seeker_max)
        if workplace in (Job.REMOTE, Job.ONSITE):
            jobs = jobs.filter(workplace=workplace)
        if visa == 'yes':
            jobs = jobs.filter(visa_sponsorship=True)
        elif visa == 'no':
            jobs = jobs.filter(visa_sponsorship=False)
        jobs = jobs.distinct()
    else:
        if skill_ids:
            recommended = (
                Job.objects
                .annotate(match_count=Count('skills', filter=Q(skills__in=skill_ids), distinct=True))
                .filter(match_count__gt=0)
                .prefetch_related('skills')
                .order_by('-match_count', '-created_at')
            )

    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['profile'] = profile
    template_data['profile_skill_ids'] = profile_skill_ids
    template_data['has_skills'] = bool(skill_ids)
    template_data['has_filters'] = has_filters
    template_data['recommended'] = recommended
    template_data['jobs'] = jobs
    template_data['filters'] = {
        'title': title,
        'skills': skills_param,
        'location': location,
        'salary_min': salary_min_param,
        'salary_max': salary_max_param,
        'workplace': workplace,
        'visa': visa,
    }
    return render(request, 'jobs/index.html', {'template_data': template_data})
