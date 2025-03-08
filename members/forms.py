from django import forms
from .models import  Profile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'date_naissance', 'telephone', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requis. Entrez une adresse email valide.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']        