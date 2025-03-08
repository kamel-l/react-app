from django import forms
from members.models import  Profile




from django import forms
from .models import Recipe, Ingredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple(),
        }

class IngredientSearchForm(forms.Form):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'date_naissance', 'telephone', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }  
        
          