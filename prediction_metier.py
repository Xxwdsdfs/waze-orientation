import requests

# URL de l'API pour faire une prédiction
url = "https://api.francetravail.io/partenaire/romeo/v2/predictionMetiers"

# Token d'accès (remplacez par votre token obtenu)
access_token = "aHO72UnDG6rL-WCFRqUdwvcwD80"

# Données à envoyer dans le corps de la requête
payload = {
    "appellations": [
        {
            "intitule": "Boucher",
            "identifiant": "123456",
            "contexte": "Commerce de détail de viandes et de produits à base de viande en magasin spécialisé"
        }
    ],
    "options": {
        "nomAppelant": "francetravail",
        "nbResultats": 2,
        "seuilScorePrediction": 0.7
    }
}

# En-têtes de la requête
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    # Envoi de la requête POST
    response = requests.post(url, json=payload, headers=headers)
    
    # Vérification de la réponse
    if response.status_code == 200:
        print("Réponse de l'API :", response.json())
    else:
        print(f"Erreur : {response.status_code}")
        print("Détails de l'erreur :", response.json())

except Exception as e:
    print("Une erreur s'est produite :", str(e))
