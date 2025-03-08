import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

BASE_URL = "https://www.cuisineaz.com/"

# Fonction pour extraire les liens des recettes
def get_recipe_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")
    pages = soup.find_all("div", class_="tile_content txt-center p20 portrait")
    links = [
        urljoin(base_url, a["href"])
        for page in pages
        for a in page.find_all("a", class_="tile_title txt-dark-gray")
    ]
    return links

# Fonction pour extraire les détails des recettes
def get_recipe_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    title = soup.find("h1", class_="recipe-title").get_text(strip=True) if soup.find("h1", class_="recipe-title") else "N/A"
    ingredients = "\n".join([ing.get_text(strip=True) for ing in soup.find_all("ul", class_="ingredient_list")])
    preparation = "\n".join([step.get_text(strip=True) for step in soup.find_all("li", class_="preparation_step")])
    time_info = soup.find("div", class_="recipe_time_information_container")
    time = time_info.get_text(strip=True) if time_info else "N/A"

    # Extraction de l'image
    image_tag = soup.find("img", class_="recipe-image")
    image_url = urljoin(url, image_tag["src"]) if image_tag and image_tag.get("src") else "N/A"

    return title, ingredients, time, preparation, image_url

# Récupération des liens
recipe_links = get_recipe_links(BASE_URL)

# Récupération des données des recettes
recipes = [get_recipe_details(link) for link in recipe_links]

# Export CSV
with open("recipes.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Ingredients", "Time", "Preparation", "Image URL"])
    writer.writerows(recipes)

print("Extraction terminée. Les données ont été enregistrées dans 'recipes.csv'.")
