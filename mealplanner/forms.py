
from django import forms
from .models import Meal
from recipe.models import Recipe

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['day_of_week', 'meal_type', 'recipe']
        widgets = {
            'day_of_week': forms.Select(choices=Meal.DAY_CHOICES),
            'meal_type': forms.Select(choices=Meal.MEAL_TYPE_CHOICES),
            'recipe': forms.Select(choices=[(recipe.id, recipe.name) for recipe in Recipe.objects.all()]),
        }