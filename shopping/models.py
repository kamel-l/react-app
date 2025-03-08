from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.
class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name="Utilisateur"
    )
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Liste de courses"
        verbose_name_plural = "Listes de courses"
        ordering = ['-created_at']

    def __str__(self):
        return f"Liste du {self.start_date} au {self.end_date}"

class ShoppingItem(models.Model):
    
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Liste de courses"
    )
    name = models.CharField(max_length=100, verbose_name="Nom")
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Quantité"
    )
    unit = models.CharField(max_length=20, verbose_name="Unité")
    checked = models.BooleanField(default=False, verbose_name="Coché")
    manual_entry = models.BooleanField(
        default=False,
        verbose_name="Ajout manuel"
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['name']

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"