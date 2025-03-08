import csv
import re
import ast  # Pour convertir une chaîne en une structure Python (comme un dict)

from django.contrib.auth.models import User
from django.db import transaction
from recipe.models import Recipe, Ingredient, Instruction

def nettoyer_temps(temps_str):
    # Extrait les nombres du format "Total :1 h 30 min"
    match = re.search(r'(\d+)\s*h\s*(\d*)', temps_str)
    if match:
        heures = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return heures * 60 + minutes
    return 30  # Valeur par défaut en minutes



def extraire_etapes(preparation_str):
    # Sépare les étapes marquées par "Étape X"
    etapes = re.split(r'Étape \d+', preparation_str)[1:]  # Ignore le premier split vide
    return [etape.strip() for etape in etapes if etape.strip()]

def importer_csv(chemin_fichier_csv, utilisateur_id=1):
    try:
        user = User.objects.get(id=utilisateur_id)
        
        with open(chemin_fichier_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if not row['Title'] or row['Title'] == 'N/A':  # Ignorer les lignes vides
                    continue
                    
                try:
                    with transaction.atomic():
                        # Créer la recette
                        recipe = Recipe.objects.create(
                            name=row['Title'],
                            prep_time=nettoyer_temps(row['Time_prep']),
                            cook_time= nettoyer_temps(row['Time_cook']),
                            servings=4,  # Valeur par défaut
                            category=row['Category'],
                            created_by=user,
                            description=row['Description']  # Résumé de la préparation
                        )
                        
                        # Traiter les ingrédients
                        ingredients = row['Ingredients']
                        dictionnaire = ast.literal_eval(ingredients)  # Conversion sécurisée
                        row['Ingredients'] = dictionnaire  # Remplace la chaîne par un vrai dict
                        for name, quantity in dictionnaire.items():
                            Ingredient.objects.create(
                                user=user,
                                recipe=recipe,
                                name=name,
                                quantity=quantity
                            )

                        
                        # Traiter les étapes de préparation
                        etapes = extraire_etapes(row['Preparation'])
                        for i, etape in enumerate(etapes, 1):
                            Instruction.objects.create(
                                recipe=recipe,
                                step_number=i,
                                description=etape
                            )
                        
                        print(f"Recette '{recipe.name}' importée avec succès!")
                
                except Exception as e:
                    print(f"Erreur lors de l'importation de la recette '{row.get('Title', 'inconnue')}' : {e}")
                    continue
                    
    except Exception as e:
        print(f"Erreur générale lors de l'importation : {e}")

# Utilisation
if __name__ == "__main__":
    importer_csv('recipe/management/commands/15_idées_de_plats.csv', utilisateur_id=1)