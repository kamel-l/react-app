from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, DetailView, CreateView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from collections import defaultdict

from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from datetime import datetime, timedelta
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MealPlans
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from recipe.models import Recipe
from typing import Dict, List, Optional
from django.db.models import Prefetch, Q, QuerySet


# Create your views here.
def get_week_dates(date):
    start = date - timedelta(days=date.weekday())
    return [start + timedelta(days=i) for i in range(7)]



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import MealPlans
import json
from datetime import datetime, timedelta

@login_required
def weekly_meal_planner(request):
    if request.method == 'GET':
        # Récupérer le décalage de la semaine depuis les paramètres de la requête
        week_offset = int(request.GET.get('week_offset', 0))
        
        # Calculer la plage de dates de la semaine
        today = datetime.today()
        first_day_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        last_day_of_week = first_day_of_week + timedelta(days=6)
        
        start_date = first_day_of_week.strftime('%Y-%m-%d')
        end_date = last_day_of_week.strftime('%Y-%m-%d')
        
        # Récupérer les repas planifiés pour la semaine
        meal_plans = MealPlans.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).select_related('recipe')
        
        # Préparer les données pour le template
        meal_plans_data = []
        for meal in meal_plans:
            meal_plans_data.append({
                'id': meal.id,
                'meal_type': meal.meal_type,
                'date': meal.date.strftime('%Y-%m-%d'),
                'recipe': {
                    'name': meal.recipe.name,
                }
            })
        
        return render(request, 'mealplanner.html', {
            'meal_plans': meal_plans_data,
            'start_date': start_date,
            'end_date': end_date,
            'week_offset': week_offset,
        })   

def change_week(request):
    direction = request.GET.get('direction')
    current_week = datetime.strptime(request.GET.get('current_week'), '%Y-%m-%d')
    
    if direction == 'prev':
        new_date = current_week - timedelta(days=7)
    else:
        new_date = current_week + timedelta(days=7)
        
    return JsonResponse({
        'redirect_url': f'/meal-planner/?date={new_date.strftime("%Y-%m-%d")}'
    })
    
import json
  
def add_meal(request):
        data = json.loads(request.body)
        print(data)
        recipe_id = data.get('recipe_id')
        day = data.get('date')
        meal_type = data.get('meal_type')
        # Récupérer d'abord l'instance de Recipe
        recipe = Recipe.objects.get(id=data['recipe_id'])

        if day and meal_type and recipe_id:
            try:
                # recipe = Recipe.objects.get(id=recipe_id)
                MealPlans.objects.create(
                    date=day,
                    meal_type=meal_type,
                    recipe=recipe,
                    user = request.user
                    )
                return JsonResponse({'success': True})
            except Recipe.DoesNotExist:
                print("Recette introuvable.")
                return JsonResponse({'success': False, 'error': 'Recipe not found'})
        else:
            print("Données manquantes.")
            return JsonResponse({'success': False, 'error': 'Missing data'})

def delete_meal(request, id):
    if request.method == "POST":
        meal = get_object_or_404(MealPlans, id=id)
        meal.delete()
        messages.success(request, "La recette a été supprimée avec succès.")
    return redirect('mealplanner')


# Gestionnaire de planification de repas optimisé
class MealPlanningManager:
    """Gestionnaire pour la planification des repas"""
    
    def __init__(self, user):
        self.user = user

    def get_week_plan(self, start_date: datetime) -> Dict:
        """Récupère le plan de la semaine"""
        end_date = start_date + timedelta(days=6)
        
        meals = MealPlans.objects.filter(
            user=self.user,
            date__range=[start_date, end_date]
        ).select_related('recipe')\
         .prefetch_related('recipe__ingredient_set')
        
        return self._organize_meals_by_day(meals)

    def _organize_meals_by_day(self, meals: QuerySet) -> Dict:
        """Organise les repas par jour"""
        organized_meals = defaultdict(lambda: defaultdict(dict))
        
        for meal in meals:
            organized_meals[meal.date.strftime('%Y-%m-%d')][meal.meal_type] = {
                'recipe': meal.recipe,
                'id': meal.id
            }
            
        return organized_meals    