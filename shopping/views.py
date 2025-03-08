from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import ShoppingItem, ShoppingList
from mealplanner.models import MealPlans
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
import json
from collections import defaultdict
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipe.models import Ingredient


# Create your views here.
def get_current_week_start():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de la semaine
    return start_of_week





@login_required
def shopping(request):
    """
    Vue pour afficher et gérer la liste de courses basée sur les repas planifiés
    """
    # Récupérer les repas planifiés de l'utilisateur pour la semaine en cours
    start_date = get_current_week_start()
    end_date = start_date + timedelta(days=6)
    meals_planned = MealPlans.objects.all()
  
    
    shopping_list = ShoppingList.objects.filter(
            user=request.user,
            start_date=start_date,
            end_date=end_date
        ).first()
    manual_items = ShoppingItem.objects.filter(
        shopping_list=shopping_list,
        manual_entry=True
    ).order_by('name')
   
    
    planned_meals = MealPlans.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).select_related('user')
   
    # Associer chaque repas planifié avec ses ingrédients
    meals_with_ingredients = []
   
    for meal in planned_meals:
        if meal.recipe:  # Vérifiez que la recette existe
            ingredients = [
                {
                    'name': ingredient.name,
                    'quantity': ingredient.quantity
                }
                for ingredient in meal.recipe.ingredient_set.all()
            ]
            meals_with_ingredients.append({
                'meal': meal,
                'ingredients': ingredients
            })
    
    
    # Créer un dictionnaire pour stocker les ingrédients  
    return render(request, 'shopping.html', {
        'meals_with_ingredients': meals_with_ingredients,
        'planned_meals': planned_meals,
        'meals_planned': meals_planned,
        'manual_items': manual_items,
      

    })
    



@require_http_methods(["POST"])
@login_required
def clear_shopping_list(request):
    """
    Vide la liste de courses personnalisée
    """
    request.session['custom_shopping_items'] = []
    return JsonResponse({'success': True})



@login_required
@require_http_methods(["POST"])
def sync_with_planning(request):
    """
    Synchronise la liste de courses avec les repas planifiés de la semaine
    """
    try:
        # Obtenir la date de début de la semaine
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        # Récupérer tous les repas planifiés pour la semaine
        ingredients = Ingredient.objects.filter(
            user=request.user,
           
        ).select_related('user')

        # Agréger les ingrédients
        ingredients_dict = defaultdict(float)
       
        for ingredient in ingredients:
                key = (ingredient.name, ingredient.unit)
                ingredients_dict[key] += float(ingredient.quantity)
       
        # Sauvegarder dans la session
        shopping_list = [
            {
                'name': name,
                'quantity': round(quantity, 2),
                'unit': unit,
                'from_planning': True
            }
            for (name, unit), quantity in ingredients_dict.items()
        ]
        print(shopping_list)
        request.session['shopping_list'] = shopping_list
        
        messages.success(request, "Liste de courses synchronisée avec le planning")
        return JsonResponse({'success': True})

    except Exception as e:
        messages.error(request, f"Erreur lors de la synchronisation : {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def add_custom_item(request):
    """Add a custom item to shopping list"""
    try:
        data = json.loads(request.body)
        print(data)
        
        # Validate required data
        if not all(key in data for key in ['name', 'quantity']):
            return JsonResponse({
                'success': False, 
                'error': 'Name and quantity are required'
            })
        
         # Get or create shopping list for current week
        start_date = get_current_week_start()
        end_date = start_date + timedelta(days=6)
        
        # Get most recent list or create new one
        try:
            shopping_list = ShoppingList.objects.filter(
                user=request.user,
                start_date=start_date,
                end_date=end_date
            ).latest('created_at')
        except ShoppingList.DoesNotExist:
            shopping_list = ShoppingList.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date
            )
        print(shopping_list)
      
       
        ShoppingItem.objects.create(
                   shopping_list=shopping_list,
                   name=data['name'].strip(),
                   quantity=float(data['quantity']),
                   unit=data.get('unit', ''),
                   manual_entry=True
                )
        return JsonResponse({
            'success': True,
            'message': 'Item added successfully'
        }) 


    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid quantity value'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
        
        
@login_required
@require_http_methods(["POST"])
def delete_shopping_item(request, item_id):
    """Delete an item from shopping list"""
    try:
        # Get item from database
        item = ShoppingItem.objects.get(id=item_id)
        
        # Check if user owns the shopping list
        if item.shopping_list.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            })
            
        # Delete item
        item.delete()
        messages.success(request, 'Item deleted successfully !')
        return redirect('shopping')
        
      
        
    except ShoppingItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
@login_required
@require_http_methods(["POST"])
def update_shopping_item(request, item_id):
    """
    Met à jour les informations d'un article
    """
    try:
        data = json.loads(request.body)
        shopping_list = request.session.get('shopping_list', [])
        
        if 0 <= item_id < len(shopping_list):
            item = shopping_list[item_id]
            item['quantity'] = float(data.get('quantity', item['quantity']))
            item['unit'] = data.get('unit', item['unit'])
            item['name'] = data.get('name', item['name'])
            
            request.session['shopping_list'] = shopping_list
            return JsonResponse({'success': True})
            
        return JsonResponse({'success': False, 'error': 'Article non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def clear_shopping_list(request):
    """
    Vide la liste de courses
    """
    request.session['shopping_list'] = []
    messages.success(request, "La liste de courses a été vidée")
    return JsonResponse({'success': True})

@login_required
def export_shopping_list(request):
    """
    Exporte la liste de courses au format texte
    """
    shopping_list = request.session.get('shopping_list', [])
    
    # Grouper par catégorie
    categories = defaultdict(list)
    for item in shopping_list:
        categories[item.get('category', 'autres')].append(item)
    
    # Générer le contenu
    content = "LISTE DE COURSES\n\n"
    for category, items in categories.items():
        content += f"=== {category.upper()} ===\n"
        for item in items:
            content += f"- {item['name']}: {item['quantity']} {item['unit']}\n"
        content += "\n"
    
    # Créer la réponse HTTP
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="liste_courses.txt"'
    
    return response
from typing import Dict, List, Optional
from mealplanner.views import MealPlanningManager

# Gestionnaire de liste de courses optimisé
class ShoppingListManager:
    """Gestionnaire pour les listes de courses"""
    
    def __init__(self, user):
        self.user = user

    def generate_shopping_list(self, start_date: datetime) -> List[Dict]:
        """Génère la liste de courses pour la semaine"""
        meal_manager = MealPlanningManager(self.user)
        week_plan = meal_manager.get_week_plan(start_date)
        
        ingredients = defaultdict(float)
        
        for day_meals in week_plan.values():
            for meal in day_meals.values():
                if meal.get('recipe'):
                    for ingredient in meal['recipe'].ingredient_set.all():
                        key = (ingredient.name, ingredient.unit)
                        ingredients[key] += float(ingredient.quantity)

        return [
            {
                'name': name,
                'quantity': round(quantity, 2),
                'unit': unit,
                'category': self._detect_category(name)
            }
            for (name, unit), quantity in ingredients.items()
        ]

    @staticmethod
    def _detect_category(ingredient_name: str) -> str:
        """Détecte la catégorie d'un ingrédient"""
        # Logique de détection de catégorie ici
        pass
