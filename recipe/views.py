from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeForm, IngredientSearchForm
from django.contrib import messages
from .models import Recipe, Instruction, Ingredient,  Review, Comments_recipe
from .services import RecipeService
from django.views.generic import ListView
from django.db.models import Q, QuerySet
from django.core.cache import cache
from typing import Dict





def home(request):
    return render(request, 'home.html')


@login_required
def recipes(request):
    return render(request, 'recipes.html')



def create_recipe_with_relations(data, user, image=None):
    """Create recipe with validation"""
    # Validate required fields
    required_fields = ['name', 'description', 'prep_time', 'cook_time', 'servings', 'category']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"{field.replace('_', ' ').title()} is required")
    """Create recipe with ingredients and instructions"""
    try:
        # Validate image if provided
        if image:
            validate_image(image)
            
        # Create base recipe
        recipe = Recipe.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            prep_time=int(data.get('prep_time', 0)),
            cook_time=int(data.get('cook_time', 0)),
            servings=int(data.get('servings', 1)),
            category=data.get('category'),
            visibility=data.get('visibility', 'private'),
            created_by=user,
            image=image
        )

        # Add ingredients
        ingredient_names = data.getlist('ingredient_name[]')
        ingredient_quantities = data.getlist('ingredient_quantity[]')
                
                
                # Création d'une liste de quantités vides si nécessaire
        if not ingredient_quantities:
            ingredient_quantities = [" "] * len(ingredient_names)
                # Si les quantités sont moins nombreuses que les noms, compléter avec des espaces
        elif len(ingredient_quantities) < len(ingredient_names):
                    ingredient_quantities.extend([" "] * (len(ingredient_names) - len(ingredient_quantities)))

        for i in range(len(ingredient_names)):
                    if ingredient_names[i].strip():  # Vérifie seulement si le nom n'est pas vide
                        Ingredient.objects.create(
                            recipe=recipe,
                            name=ingredient_names[i].strip(),
                            quantity=ingredient_quantities[i].strip() if ingredient_quantities[i].strip() else " ",
                            user=user
                        )


        # Add instructions
         # Traitement des instructions
        instructions = data.getlist('instructions[]')
        for index, instruction_text in enumerate(instructions, start=1):
                if instruction_text.strip():
                    Instruction.objects.create(
                            recipe=recipe,
                            step_number=index,
                            description=instruction_text.strip()
                        )


        return recipe

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error creating recipe: {str(e)}")

def validate_image(image):
    if image:
        if image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("L'image ne doit pas dépasser 5MB")
        if image.content_type not in ['image/jpeg', 'image/png']:
            raise ValidationError("Format d'image non supporté")

@login_required
@require_http_methods(["POST"])
def update_recipe_image(request, recipe_id):
    """Update recipe image only"""
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id, created_by=request.user)
        
        if 'image' in request.FILES:
            # Validate new image
            validate_image(request.FILES['image'])
            
            # Delete old image if exists
            if recipe.image:
                recipe.image.delete()
                
            # Save new image
            recipe.image = request.FILES['image']
            recipe.save()
            
            messages.success(request, 'Recipe image updated successfully')
        else:
            messages.error(request, 'No image file provided')
            
        return redirect('RecipesListsViews')
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('RecipeDetailView', recipe_id=recipe_id)
    except Exception as e:
        messages.error(request, f"Error updating image: {str(e)}")
        return redirect('RecipesListsViews')
    except Exception as e:
        import traceback
        traceback.print_exc()  # Affiche la trace complète dans les logs
        return JsonResponse({'success': False, 'error': 'Erreur serveur: ' + str(e)})
            
            
            
def clean_ingredient_data(ingredient_names, ingredient_quantities):
    return [
        (name, quantity) 
        for name, quantity in zip(ingredient_names, ingredient_quantities)
        if name and quantity
    ]     
    
    
       
@login_required
@require_http_methods(["GET", "POST"])
def new_recipe(request):
    """View for creating a new recipe with enhanced validation"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create recipe with current user
                recipe = create_recipe_with_relations(
                    data=request.POST,
                    user=request.user,
                    image=request.FILES.get('image')
                )
                messages.success(request, 'Recipe created successfully!')
                return redirect('RecipeDetailView', recipe_id=recipe.id)
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            
    return render(request, 'new_recipes.html', {
        'categories': Recipe.CATEGORY_CHOICES,
        'visibility_choices': Recipe.VISIBILITY_CHOICES
    })

        
def Sherche_recipes(request):
    latest_recipes = Recipe.objects.order_by('-created_at')[:6]
    return render(request, 'Sherche_recipes.html', {'recipes': latest_recipes})

@login_required
def recipe_generator(request):
    if request.method == 'POST':
        form = IngredientSearchForm(request.POST)
        if form.is_valid():
            ingredients = form.cleaned_data['ingredients']
            recipes = Recipe.objects.filter(ingredient_set__in=ingredients).distinct()
            return render(request, 'recipe_results.html', {
                'recipes': recipes,
                'form': form
            })
    else:
        form = IngredientSearchForm()
    return render(request, 'recipe_generator.html', {'form': form})


class RecipesListsViews(LoginRequiredMixin, ListView):
    template_name = 'recipes_lists.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        filters = {
            'category': self.request.GET.get('category'),
            'search': self.request.GET.get('q'),
            'visibility': 'public'  # Show only public recipes
        }
        return RecipeService.get_recipes_with_filters(filters)

@login_required
def my_recipes(request):
    filters = {
        'category': request.GET.get('category'),
        'search': request.GET.get('q'),
        'visibility': 'private',
        'user': request.user
    }
    recipes = RecipeService.get_recipes_with_filters(filters)
    return render(request, 'my_recipes.html', {'recipes': recipes})

class RecipeService:
    @staticmethod
    def get_recipes_with_filters(filters: Dict) -> QuerySet:
        """Get recipes with filters"""
        queryset = Recipe.objects.all()
        
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
            
        if filters.get('search'):
            search_query = Q(name__icontains=filters['search']) | \
                         Q(description__icontains=filters['search'])
            queryset = queryset.filter(search_query)

        # Filter by visibility
        if filters.get('visibility') == 'private':
            queryset = queryset.filter(
                visibility='private', 
                created_by=filters.get('user')
            )
        elif filters.get('visibility') == 'public':
            queryset = queryset.filter(visibility='public')
            
        return queryset.select_related('created_by')\
                      .prefetch_related('ingredient_set', 'instruction_set')

import re
import ast   
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
import json

    
def RecipeDetailView(request, recipe_id):
    """
    Vue détail d'une recette
    """
    # Récupérer la recette spécifique ou renvoyer une 404 si elle n'existe pas
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    
    recipe.vues += 1
    recipe.save()
   
    instructions = list(recipe.instruction_set.order_by('step_number').values('step_number', 'description'))
    ingredients = list(recipe.ingredient_set.values('name', 'quantity'))
    
    

    midpoint = len(ingredients) // 2
    left_column = ingredients[:midpoint]
    right_column = ingredients[midpoint:]
    
    def get_object(self, queryset=None):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        # Vérifiez si l'utilisateur a accès à la recette
        if not recipe.is_public and recipe.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to view this recipe.")
        return recipe
 
    
    # Rendre le template avec le contexte
    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'instructions': instructions,
        'left_column': left_column,
        'right_column': right_column
    })

###############################################################
def delete_recipe(request, id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=id)
        recipe.delete()
        messages.success(request, "La recette a été supprimée avec succès.")
    return redirect('RecipesListsViews')
           
def get_current_week_start():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de la semaine
    return start_of_week


CACHE_TIMEOUT = 3600  # 1 heure
ITEMS_PER_PAGE = 12



def get_recipe_ingredients(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    ingredients = [
        {
            'name': ingredient.name, 
            'quantity': ingredient.quantity, 
            'unit': ingredient.unit
        } for ingredient in recipe.ingredients.all()
    ]
    return JsonResponse({'ingredients': ingredients})  
    #return render(request, 'shopping.html', {'ingredients': ingredients, 'recipe': recipe})   
  

    


@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            form.save_m2m()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})


# Constantes
CACHE_TIMEOUT = 3600  # 1 heure
ITEMS_PER_PAGE = 12

# Mixins et classes de base
class UserSpecificMixin(LoginRequiredMixin):
    """Mixin pour filtrer les objets par utilisateur"""
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

class CacheMixin:
    """Mixin pour la mise en cache des vues"""
    cache_timeout = CACHE_TIMEOUT

    def get_cache_key(self) -> str:
        return f"{self.__class__.__name__}_{self.request.user.id}_{self.request.path}"

    def get(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        response = cache.get(cache_key)
        
        if response is None:
            response = super().get(request, *args, **kwargs)
            cache.set(cache_key, response, self.cache_timeout)
            
        return response

# Vues optimisées
class OptimizedRecipeListView(UserSpecificMixin, CacheMixin, ListView):
    """Vue optimisée pour la liste des recettes"""
    model = Recipe
    template_name = 'recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        filters = {
            'category': self.request.GET.get('category'),
            'search': self.request.GET.get('q')
        }
        return RecipeService.get_recipes_with_filters(self.request.user, filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = cache.get_or_set(
            f'categories_{self.request.user.id}',
            lambda: list(Recipe.objects.filter(created_by=self.request.user)
                        .values_list('category', flat=True).distinct()),
            CACHE_TIMEOUT
        )
        return context



@login_required
def edit_recipe(request, recipe_id):
    """Edit an existing recipe"""
    recipe = get_object_or_404(Recipe, id=recipe_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update base recipe fields
                recipe.name = request.POST.get('name')
                recipe.description = request.POST.get('description')
                recipe.preparation_time = int(request.POST.get('prep_time'))
                recipe.cooking_time = int(request.POST.get('cook_time'))
                recipe.servings = int(request.POST.get('servings'))
                recipe.category = request.POST.get('category')
                recipe.visibility = request.POST.get('visibility')
                
                # Handle image update
                if request.FILES.get('image'):
                    validate_image(request.FILES['image'])
                    recipe.image = request.FILES['image']
                
                recipe.save()
                
                # Update ingredients
                recipe.ingredient_set.all().delete()
                ingredient_names = request.POST.getlist('ingredient_name')
                ingredient_quantities = request.POST.getlist('ingredient_quantity')
                
                for name, quantity in zip(ingredient_names, ingredient_quantities):
                    if name and quantity:
                        Ingredient.objects.create(
                            recipe=recipe,
                            name=name.strip(),
                            quantity=quantity,
                            user=request.user  # Added missing user field
                        )
                
                # Mise à jour des instructions
                recipe.instruction_set.all().delete()
                instructions = request.POST.getlist('instructions')
                for i, instruction_text in enumerate(instructions, 1):
                    if instruction_text.strip():
                        Instruction.objects.create(
                            recipe=recipe,
                            step_number=i,
                            description=instruction_text.strip()  # Changé 'text' en 'instruction'
                        )
                
                messages.success(request, 'Recipe successfully updated!')
                return redirect('RecipeDetailView', recipe_id=recipe.id)
                
        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
        except ValueError as e:
            messages.error(request, "Format error: Please check the numerical values entered")
        except Exception as e:
            messages.error(request, f"Error updating recipe: {str(e)}")
    
    return render(request, 'edit_recipe.html', {
        'recipe': recipe,
        'categories': Recipe.CATEGORY_CHOICES,
        'visibility_choices': Recipe.VISIBILITY_CHOICES,
    })
    
    
def ingredient_sherch(request):
    return render(request, 'recipe_search.html')



import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Clé API Spoonacular
SPOONACULAR_API_KEY = settings.SPOONACULAR_API_KEY

@require_http_methods(["GET"])
def find_recipes_by_ingredients(request):
    # Récupérer les ingrédients depuis les paramètres de la requête
    ingredients = request.GET.get('ingredients', '')
    
    if not ingredients:
        return JsonResponse({'error': 'No ingredients provided'}, status=400)
    
    # URL de l'API Spoonacular pour rechercher des recettes par ingrédients
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    
    # Paramètres de la requête
    params = {
        'ingredients': ingredients,
        'number': 10,  # Nombre de recettes à retourner
        'apiKey': SPOONACULAR_API_KEY,
    }
    
    try:
        # Faire la requête à l'API Spoonacular
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lève une exception si la requête échoue
        recipes = response.json()
        for key in recipes:
            print(key['image'])
                
        
        
        # Retourner les recettes trouvées
        return JsonResponse({'recipes': recipes})

    
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        return JsonResponse({'error': str(e)}, status=500)
    
    
def recipe_detail_view(request, recipe_id):
    # Construire l'URL de l'API pour obtenir les détails de la recette
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': SPOONACULAR_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Vérifie s'il y a une erreur HTTP
        recipe_data = response.json()
        
        return render(request, 'recipe_detail.html', {'recipe': recipe_data})

    except requests.exceptions.RequestException as e:
        return render(request, 'recipe_detail.html', {'error': f"Erreur : {str(e)}"})  
    
    
from .models import Notification

# afficher les notifications d'un utilisateur

@login_required
def notifications(request):
    comments = Comments_recipe.objects.all()
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = user_notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {
        'notifications': user_notifications,
        'unread_notifications_count': unread_notifications_count,
        'comments': comments,
    }) 
      

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
@require_http_methods(["POST"])
def mark_notification_as_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, 
                                       id=notification_id, 
                                       recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_as_read(request):
    try:
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.contrib.auth.models import User
from .models import Notification

# Ajouter des notifications dans votre application

def create_recipe_notification(recipe):
    users = User.objects.filter()  # Exemple : utilisateurs qui suivent l'auteur
    for user in users:
        Notification.objects.create(
            user=user,
            message=f"New recipe by {recipe.created_by.username}: {recipe.name}",
            link=f"/recipe/{recipe.id}/"
        )


def create_comment_notification(comment):
    recipe_author = comment.recipe.created_by  # Accédez à l'auteur de la recette via le commentaire
    Notification.objects.create(
        recipient = recipe_author,
        user=recipe_author,
        message=f"Nouveau commentaire sur votre recette : {comment.recipe.name}",
        
    )
        
def create_meal_reminder_notification(user, meal):
    Notification.objects.create(
        user=user,
        message=f"Reminder: Don't forget to prepare {meal.name} for {meal.date}",
        link=f"/mealplanner/{meal.id}/"
    )    
    
from django.shortcuts import render, get_object_or_404
from .models import Comments_recipe

def comment_detail(request, recipe_id, comment_id):
    comment = get_object_or_404(Comments_recipe, id=comment_id)
    return render(request, 'comment_detail.html', {'comment': comment})   

# views.py
@login_required
def add_review(request, recipe_id):
    if request.method == 'POST':
        try:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            rating = request.POST.get('rating')
            comment_text = request.POST.get('comment')
            
            if not rating or not comment_text:
                return JsonResponse({
                    'success': False,
                    'error': 'La note et le commentaire sont obligatoires'
                })
            
            # Create comment first
            comment = Comments_recipe.objects.create(
                recipe=recipe,
                user=request.user,
                text=comment_text
            )
            
            # Create or update review
            review, created = Review.objects.update_or_create(
                recipe=recipe,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment_text
                }
            )
            
            
            return JsonResponse({
                'success': True,
                'message': 'Avis ajouté avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de l\'ajout de l\'avis : {str(e)}'
            })

@login_required
def view_comment(request, notification_id):
    if request.user.is_authenticated:
        Comments_recipe.objects.filter(user=request.user, is_read=False).update(is_read=True)
    try:
        # Get notification
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        
        # Get comment
        comment = get_object_or_404(Comments_recipe, id=notification.target_id)
       
        
        # Mark notification as read
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        
        return JsonResponse({
            'success': True,
            'comment': {
                'text': comment.text,
                'user': comment.user.username,
                'created_at': comment.created_at.strftime('%d %B %Y'),
                'recipe': comment.recipe.name,
                'notification_id': notification.id
            }
        })
        
    except Comments_recipe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Comment not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


from django.http import JsonResponse
from .models import Comments_recipe  # Assurez-vous d'importer votre modèle Comment

def unread_comments_count(request):
    if request.user.is_authenticated:
        count = Comments_recipe.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'success': True, 'count': count})
    return JsonResponse({'success': False, 'count': 0})        

from django.shortcuts import render
from django.http import JsonResponse
from .models import Comments_recipe, Recipe  # Assurez-vous d'importer vos modèles

def user_recipe_comments(request):
    if request.user.is_authenticated:
        # Récupérer les recettes créées par l'utilisateur
        user_recipes = Recipe.objects.filter(created_by=request.user)
        # Récupérer les commentaires associés à ces recettes
        comments = Comments_recipe.objects.filter(recipe__in=user_recipes).select_related('user', 'recipe')
        
        # Sérialiser les commentaires pour les renvoyer au template
        comments_data = [
            {
                'user': comment.user.username,
                'recipe': comment.recipe.name,
                'text': comment.text,
                'created_at': comment.created_at.strftime("%d %b %Y %H:%M"),
            }
            for comment in comments
        ]
        
        # Compter les commentaires non lus
        unread_count = Comments_recipe.objects.filter(recipe__in=user_recipes, is_read=False).count()
        print(unread_count)
        
        return JsonResponse({'success': True, 'comments': comments_data, 'unread_count': unread_count})
    return JsonResponse({'success': False, 'comments': [], 'unread_count': 0})