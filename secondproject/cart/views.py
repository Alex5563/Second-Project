from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from jobs.models import Job, Application
from accounts.permissions import is_recruiter, job_seeker_required
from django.contrib.auth.decorators import login_required

# Create your views here.

@job_seeker_required
@login_required
def index(request):
    if is_recruiter(request.user):
        return redirect('home.index')
    jobs_in_cart = []
    applied_ids = []
    cart = request.session.get('cart', [])
    if (cart != []):
        jobs_in_cart = Job.objects.filter(id__in=cart)
        applications = Application.objects.filter(
            user=request.user)
        for application in applications:
            applied_ids.append(application.job.id)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['jobs_in_cart'] = jobs_in_cart
    template_data['applied_ids'] = applied_ids
    return render(request, 'cart/index.html',
        {'template_data': template_data})
@job_seeker_required
@require_POST
@login_required
def add(request, id):
    get_object_or_404(Job, id=id)
    cart = request.session.get('cart', [])
    if id not in cart:
        cart.append(id)
    request.session['cart'] = cart
    return redirect('cart.index')
@job_seeker_required
@require_POST
@login_required
def remove(request, id):
    cart = request.session.get('cart', [])
    if id in cart:
        cart.remove(id)
    request.session['cart'] = cart
    return redirect('cart.index')
@job_seeker_required
@require_POST
@login_required
def clear(request):
    request.session['cart'] = []
    return redirect('cart.index')
