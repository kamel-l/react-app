from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.
class Recipe(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Privé'),
        ('public', 'Public')
    ]
    visibility = models.CharField(
        max_length=10, 
        choices=VISIBILITY_CHOICES, 
        default='public'
    )
    
    CATEGORY_CHOICES = [
        ('entree', 'Entrée'),
        ('plat', 'Plat principal'),
        ('dessert', 'Dessert'),
        ('snack', 'Collation'),
        ('autre', 'Autre'),
    ]
    
   
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    prep_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Temps de préparation (minutes)"
        
    )
    
    cook_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Temps de cuisine (minutes)")
    
        
    servings = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Nombre de portions")
    
    
    category = models.CharField(
        max_length=50,
        verbose_name="Catégorie"
    )
    image = models.ImageField(
        upload_to='media/',
        blank=True,
        null=True,
        verbose_name="Image"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Créé par"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    vues = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    def get_rating_count(self):
        return self.reviews.count()

class Ingredient(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe =models.ForeignKey(Recipe, related_name="ingredient_set", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Nom")
    quantity = models.CharField(max_length=100,verbose_name="Quantité")

    class Meta:
        verbose_name = "Ingrédient"
        verbose_name_plural = "Ingrédients"

    def __str__(self):
        return f"{self.quantity}  {self.name}"
        
        
class Instruction(models.Model):
        recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='instruction_set',
        verbose_name="Recette"
    )
        step_number = models.PositiveIntegerField(
        verbose_name="Numéro de l'étape"
    )
        description = models.TextField(
        verbose_name="Description de l'étape"
    )

        class Meta:
            verbose_name = "Étape de préparation"
            verbose_name_plural = "Étapes de préparation"
            ordering = ['step_number']

        def __str__(self):  
            return f"Étape {self.step_number} - {self.recipe.name}"

from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ['-created_at']


class Calories(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    calories = models.CharField(max_length=100,verbose_name="Quantité")

    class Meta:
        verbose_name = "Calories"

    def __str__(self):
        return f"{self.calories}  {self.name}"
    
from django.db import models
from django.contrib.auth.models import User


class Comments_recipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.recipe.name}"
    
    def save(self, *args, **kwargs):
        # Check if this is a new comment
        is_new = self._state.adding
        
        # Save the comment
        super().save(*args, **kwargs)
        
        # Create notification for new comments
        if is_new and self.recipe.created_by != self.user:
            Notification.objects.create(
                recipient=self.recipe.created_by,
                user=self.user,
                message=f"{self.user.username} a commenté votre recette {self.recipe.name}",
                target_id=self.id
            )

    @property
    def formatted_date(self):
        return self.created_at.strftime('%d %B %Y')

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @classmethod
    def get_unread_count_for_user(cls, user):
        return cls.objects.filter(recipe__created_by=user, is_read=False).count()

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.CharField(max_length=255)
    target_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.recipient.username} de {self.user.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
