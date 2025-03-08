import requests

endpoint = "https://www.cuisineaz.com/diaporamas/100-recettes-minceur-faciles-et-rapides-3836/interne/1.aspx"

get_responce = requests.get(endpoint, data={"key1": "value1", "key2": "value2"})

print(get_responce.text)