import os
from django.core.files import File
from faimilymeal.models import Recipe

import os
import django

# Remplacez 'your_project.settings' par le chemin vers votre fichier settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faimilymeal.settings')
django.setup()

def add_image_to_recipe(recipe_id, image_path):
    """
    Ajoute une image à une recette existante.
    
    :param recipe_id: ID de la recette à mettre à jour.
    :param image_path: Chemin vers l'image à ajouter.
    :return: Message de succès ou d'erreur.
    """
    # Vérifier si le fichier d'image existe
    if not os.path.exists(image_path):
        return f"Erreur : L'image '{image_path}' n'existe pas."

    try:
        # Récupérer la recette
        recipe = Recipe.objects.get(id=recipe_id)
        
        # Ouvrir le fichier d'image et l'ajouter au champ 'image'
        with open(image_path, 'rb') as img_file:
            recipe.image.save(os.path.basename(image_path), File(img_file))
        
        # Sauvegarder les modifications
        recipe.save()
        return f"L'image a été ajoutée avec succès à la recette '{recipe.name}'."
    except Recipe.DoesNotExist:
        return f"Erreur : La recette avec l'ID {recipe_id} n'existe pas."
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"

# Exemple d'utilisation
if __name__ == "__main__":
    # Remplacez par l'ID de la recette et le chemin de l'image
    RECIPE_ID = 1  # ID de la recette cible
    IMAGE_PATH = "/media/media/i28316-meringue.jpg"  # Chemin absolu ou relatif vers l'image

    # Appeler la fonction
    result = add_image_to_recipe(RECIPE_ID, IMAGE_PATH)
    print(result)
