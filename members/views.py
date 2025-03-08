from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from .forms import  ProfileUpdateForm
from recipe.models import Recipe
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import Profile, SignUpModels
from recipe.models import Comments_recipe, Notification




def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Création automatique du profil
            SignUpModels.objects.create(user=user)
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/user_signup.html', {'form': form})




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('RecipesListsViews')
        else:
            messages.error(request, 'Identifiants invalides.')
    return render(request, 'registration/login.html')



def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
        is_own_profile = request.user == profile_user
    else:
        profile_user = request.user
        is_own_profile = True
    
    # Get or create profile for the viewed user (not necessarily the logged-in user)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    # Get recipes for the viewed user
    recipes = Recipe.objects.filter(created_by=profile_user)
    
    # Calculate statistics
    total_vues = recipes.aggregate(total_vues=Sum('vues'))['total_vues'] or 0
    moyenne_vues = recipes.aggregate(avg_vues=Avg('vues'))['avg_vues'] or 0
    
    stats = {
        'total_recettes': recipes.count(),
        'total_vues': total_vues,
        'moyenne_vues_par_recette': round(moyenne_vues, 1),
        'recette_plus_vue': recipes.order_by('-vues').first(),
        'recettes_populaires': recipes.order_by('-vues')[:5],
        'date_inscription': profile_user.date_joined,
        'derniere_recette': recipes.order_by('-created_at').first(),
        'recettes_recentes': recipes.order_by('-created_at')[:5],
        'recettes_par_categorie': recipes.values('category').annotate(
            count=Count('id'),
            total_vues=Sum('vues')
        ).order_by('-count')
    }

    # Global rankings
    classement_global = Recipe.objects.all().order_by('-vues')[:10]

    # Handle profile form
    if request.method == 'POST' and is_own_profile:
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('own_profile')
    else:
        form = ProfileUpdateForm(instance=profile) if is_own_profile else None
    
    # Get comments and notifications
    comments = Comments_recipe.objects.filter(recipe__created_by=profile_user).order_by('-created_at')
    
    # Only get notifications for the logged-in user viewing their own profile
    notifications = []
    if is_own_profile:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('user').order_by('-created_at')

    context = {
        'profile': profile,
        'recipes': recipes,
        'stats': stats,
        'classement_global': classement_global,
        'form': form,
        'is_own_profile': is_own_profile,
        'comments': comments,
        'notifications': notifications,
        'user': profile_user  # Add viewed user to context
    }

    return render(request, 'profile.html', context)
#######################################################################################################################################






# Create your views here.
