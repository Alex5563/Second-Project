from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from accounts.permissions import job_seeker_required, is_recruiter
from .models import Profile, PrivacySettings
from .forms import ProfileForm, EducationFormSet, ExperienceFormSet, LinkFormSet, PrivacyForm

@job_seeker_required
def index(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    template_data = {}
    template_data['title'] = 'My Profile'
    template_data['profile'] = profile
    return render(request, 'profiles/index.html', {'template_data': template_data})

@job_seeker_required
def edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    data = request.POST if request.method == 'POST' else None

    form = ProfileForm(data, instance=profile)
    education = EducationFormSet(data, instance=profile, prefix='education')
    experience = ExperienceFormSet(data, instance=profile, prefix='experience')
    links = LinkFormSet(data, instance=profile, prefix='links')

    if request.method == 'POST':
        if all([form.is_valid(), education.is_valid(),
                experience.is_valid(), links.is_valid()]):
            form.save()
            education.save()
            experience.save()
            links.save()
            return redirect('profiles.index')

    template_data = {}
    template_data['title'] = 'Edit Profile'
    template_data['form'] = form
    template_data['formsets'] = [
        ('Education', education),
        ('Work Experience', experience),
        ('Links', links),
    ]
    return render(request, 'profiles/edit.html', {'template_data': template_data})
@job_seeker_required
def privacy(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    privacy_settings, created = PrivacySettings.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        form = PrivacyForm(request.POST, instance=privacy_settings)
        if form.is_valid():
            form.save()
            return redirect('profiles.index')
    else:
        form = PrivacyForm(instance=privacy_settings)

    template_data = {}
    template_data['title'] = 'Privacy Settings'
    template_data['form'] = form
    return render(request, 'profiles/privacy.html', {'template_data': template_data})

@login_required
def detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    privacy_settings, created = PrivacySettings.objects.get_or_create(profile=profile)
    is_owner = profile.user_id == request.user.id

    # Only the owner, or a recruiter when the profile is visible to recruiters
    if not is_owner:
        if not is_recruiter(request.user) or not privacy_settings.visible_to_recruiters:
            raise Http404

    template_data = {}
    template_data['title'] = profile.user.username
    template_data['profile'] = profile
    template_data['show'] = {
        'email': is_owner or privacy_settings.show_email,
        'skills': is_owner or privacy_settings.show_skills,
        'education': is_owner or privacy_settings.show_education,
        'experience': is_owner or privacy_settings.show_experience,
        'links': is_owner or privacy_settings.show_links,
    }
    return render(request, 'profiles/detail.html', {'template_data': template_data})