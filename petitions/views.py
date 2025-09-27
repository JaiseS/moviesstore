from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
from .models import Petition
from .forms import PetitionForm

def petition_list(request):
    # Get all petitions ordered by creation date (newest first)
    petitions = Petition.objects.all().order_by('-created_at')
    
    # Prefetch related votes to avoid N+1 queries
    if request.user.is_authenticated:
        # For authenticated users, prefetch their votes
        petitions = petitions.prefetch_related(
            models.Prefetch('votes', queryset=User.objects.filter(pk=request.user.pk))
        )
    
    return render(request, 'petitions/petition_list.html', {
        'petitions': petitions,
    })

@login_required
def create_petition(request):
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.user = request.user
            petition.save()
            messages.success(request, 'Your petition has been created!')
            return redirect('petitions:list')
    else:
        form = PetitionForm()
    return render(request, 'petitions/create_petition.html', {'form': form})

from django.views.decorators.csrf import ensure_csrf_cookie

@login_required
def vote_petition(request, pk):
    print("Vote endpoint hit!")
    print(f"Request method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"POST data: {request.POST}")
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        petition = Petition.objects.get(pk=pk)
        print(f"Found petition: {petition}")
    except Petition.DoesNotExist:
        print(f"Petition {pk} not found")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Petition not found'}, status=404)
        messages.error(request, 'Petition not found')
        return redirect('petitions:list')
        
    user = request.user
    print(f"User: {user}")
    
    if petition.user == user:
        print("User tried to vote on their own petition")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'You cannot vote on your own petition'}, status=400)
        messages.error(request, 'You cannot vote on your own petition')
        return redirect('petitions:list')
    
    # Toggle vote
    if petition.votes.filter(id=user.id).exists():
        print("Removing vote")
        petition.votes.remove(user)
        petition.vote_count = petition.votes.count()  # Update count
        petition.save()  # This will trigger the save() method to update vote_count
        voted = False
    else:
        print("Adding vote")
        petition.votes.add(user)
        petition.vote_count = petition.votes.count()  # Update count
        petition.save()  # This will trigger the save() method to update vote_count
        voted = True
    
    # Refresh the petition to get the updated vote count
    petition.refresh_from_db()
    total_votes = petition.vote_count
    print(f"New vote count: {total_votes}")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {
            'success': True,
            'total_votes': total_votes,
            'voted': voted,
            'petition_id': str(pk)
        }
        print(f"Sending JSON response: {response_data}")
        return JsonResponse(response_data)
    
    # For non-AJAX requests, redirect back to the list page
    messages.success(request, 'Your vote has been recorded!')
    return redirect('petitions:list')
