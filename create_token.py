import requests

def generate_token(client_id, client_secret):
    # URL pour générer le token
    url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"

    # Données nécessaires pour l'authentification
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "api_romeov2"
    }

    # En-têtes de la requête
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # Envoi de la requête POST
        response = requests.post(url, data=payload, headers=headers)
        
        # Vérification de la réponse
        if response.status_code == 200:
            # Extraction du token d'accès
            token = response.json().get("access_token")
            print("Token généré avec succès :", token)
            return token
        else:
            print(f"Erreur : {response.status_code}")
            print("Détails de l'erreur :", response.json())
            return None

    except Exception as e:
        print("Une erreur s'est produite :", str(e))
        return None

# Exemple d'appel de la fonction
client_id = "PAR_wazeorientation_574357eec36312ebe52b43fd301e177cd49c8480899c9a82402d394f685cfb94"  # Remplacez par votre ID client
client_secret = "a2adc3ef3712d29d93e72718b698c063a63f2153f23a3f1557ca71e0d43c3bfb"  # Remplacez par votre clé secrète

# Appel de la fonction pour générer le token
access_token = generate_token(client_id, client_secret)

if access_token:
    print("Token obtenu :", access_token)
else:
    print("Échec de l'obtention du token.")
