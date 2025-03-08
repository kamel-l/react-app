import os
from django.core.files import File
from recipe.models import Recipe
from django.utils.text import slugify
import shutil
from django.conf import settings

def associer_images_recettes(dossier_images):
    """
    Associe les images du dossier aux recettes existantes
    """
    # S'assurer que le dossier media existe
    media_path = os.path.join(settings.MEDIA_ROOT, 'media')
    os.makedirs(media_path, exist_ok=True)
    
    # Récupérer toutes les recettes
    recettes = Recipe.objects.all()
    
    # Extensions d'images supportées
    extensions_valides = ['.jpg', '.jpeg', '.png', '.gif']
    
    for recette in recettes:
        # Créer une version "slugifiée" du nom de la recette pour la recherche
        nom_slugifie = slugify(recette.name)
        
        # Chercher une image correspondante
        image_trouvee = None
        
        for fichier in os.listdir(dossier_images):
            nom_fichier, extension = os.path.splitext(fichier.lower())
            if extension in extensions_valides:
                # Vérifier si le nom du fichier correspond à la recette
                if (slugify(nom_fichier) == nom_slugifie or 
                    nom_slugifie in slugify(nom_fichier) or 
                    slugify(nom_fichier) in nom_slugifie):
                    image_trouvee = fichier
                    break
        
        if image_trouvee:
            # Chemin complet vers l'image source
            chemin_source = os.path.join(dossier_images, image_trouvee)
            
            # Créer un nouveau nom de fichier unique
            nouveau_nom = f"{nom_slugifie}{os.path.splitext(image_trouvee)[1]}"
            chemin_destination = os.path.join(media_path, nouveau_nom)
            
            try:
                # Copier l'image vers le dossier media
                shutil.copy2(chemin_source, chemin_destination)
                
                # Mettre à jour le champ image de la recette
                with open(chemin_destination, 'rb') as f:
                    recette.image.save(nouveau_nom, File(f), save=True)
                
                print(f"Image associée avec succès à la recette : {recette.name}")
                
            except Exception as e:
                print(f"Erreur lors de l'association de l'image pour {recette.name}: {str(e)}")
        else:
            print(f"Aucune image trouvée pour la recette : {recette.name}")

def nettoyer_nom_fichier(nom):
    """
    Nettoie le nom de fichier en retirant les caractères spéciaux
    """
    return ''.join(c for c in nom if c.isalnum() or c in (' ', '-', '_')).strip()

# Exemple d'utilisation
if __name__ == "__main__":
    DOSSIER_IMAGES = 'C:/Users/kamel/PycharmProjects/faimilyapp/faimilymeal/management/commands/image_recette'
   
    associer_images_recettes(DOSSIER_IMAGES)