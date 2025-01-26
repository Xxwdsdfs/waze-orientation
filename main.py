from create_token import generate_token
from prediction_competence import search_competence

# Exemple d'appel de la fonction pour générer un token et faire une recherche
if __name__ == "__main__":
    client_id = "PAR_wazeorientation_574357eec36312ebe52b43fd301e177cd49c8480899c9a82402d394f685cfb94"  # Remplacez par votre ID client
    client_secret = "a2adc3ef3712d29d93e72718b698c063a63f2153f23a3f1557ca71e0d43c3bfb"  # Remplacez par votre clé secrète

    # Appel de la fonction pour générer un token
    token = generate_token(client_id, client_secret)

    if token:
        competences = [
            {
                "intitule": "faire du pain",
                "identifiant": "123456"
            }
        ]

        # Appel de la fonction pour rechercher des compétences
        resultat = search_competence(token, competences)

        if resultat:
            print("Résultat de la recherche :", resultat)
        else:
            print("Échec de la recherche des compétences.")
    else:
        print("Échec de la génération du token.")