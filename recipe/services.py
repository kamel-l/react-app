from typing import Dict
from django.db.models import QuerySet, Q
from .models import Recipe
from mealplanner.models import MealPlans
from datetime import datetime, timedelta
from collections import defaultdict

class RecipeService:
    """Service pour la gestion des recettes"""

    @staticmethod
    def get_recipes_with_filters(user, filters: Dict) -> QuerySet:
        queryset = Recipe.objects.filter(created_by=user)

        if filters.get('category'):
            queryset = queryset.filter(category__icontains=filters['category'])

        if filters.get('search'):
            search_query = Q(name__icontains=filters['search']) | Q(description__icontains=filters['search'])
            queryset = queryset.filter(search_query)

        return queryset.select_related('created_by').prefetch_related('ingredient_set')

    @staticmethod
    def get_week_plan(user) -> Dict:
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=6)
        meals = MealPlans.objects.filter(user=user, date__range=[start_date, end_date]).select_related('recipe')
        return RecipeService._organize_meals_by_day(meals)

    @staticmethod
    def _organize_meals_by_day(meals: QuerySet) -> Dict:
        organized_meals = defaultdict(lambda: defaultdict(dict))
        for meal in meals:
            organized_meals[meal.date.strftime('%Y-%m-%d')][meal.meal_type] = {'recipe': meal.recipe, 'id': meal.id}
        return organized_meals
