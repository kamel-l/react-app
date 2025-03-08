from django.db import models
from django.contrib.auth.models import User
from recipe.models import Recipe


# Create your models here.
class MealPlans(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE) # Ajustez selon votre modèle Recipe
    date = models.DateField()
    meal_type = models.CharField(max_length=20)
    
    
    
    def __str__(self):
        return f"{self.date} - {self.meal_type}: {self.recipe}"
    
    
class Meal(models.Model):
    DAY_CHOICES = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche'),
    ]

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Petit déjeuner'),
        ('lunch', 'Déjeuner'),
        ('dinner', 'Dîner'),
    ]

    day_of_week = models.CharField(choices=DAY_CHOICES, max_length=9)
    meal_type = models.CharField(choices=MEAL_TYPE_CHOICES, max_length=9)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day_of_week} - {self.get_meal_type_display()} - {self.recipe.name}"
