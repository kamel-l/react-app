import json
from ...models import Calories

# Charger le fichier JSON
with open('C:/Users/kamel/PycharmProjects/faimilyapp/recipe/management/commands/tableaux.json', 'r', encoding='utf-8') as fichier:
    data = json.load(fichier)
    
for tableau in data:
    numero_tableau = tableau['tableau']
    for ligne in tableau['lignes']:
        ingredient = ligne[0]
        kalore = ligne[1]    
    
        calories = Calories.objects.create(
                            name=ligne[0],
                            calories =ligne[1] 
                        )    

