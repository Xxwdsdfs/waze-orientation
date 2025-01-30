from create_token import generate_token
from prediction_competence import search_competence

def main():
    client_id = "PAR_wazeorientation_574357eec36312ebe52b43fd301e177cd49c8480899c9a82402d394f685cfb94"  
    client_secret = "a2adc3ef3712d29d93e72718b698c063a63f2153f23a3f1557ca71e0d43c3bfb"  

    # Génération du token
    token = generate_token(client_id, client_secret)
    if not token:
        print("Échec de la génération du token.")
        return
    
    # Demande de l'action à l'utilisateur
    action = input("Entrez une action : ")
    if not action:
        print("Vous devez entrer une action valide.")
        return
    
    competences = [{"intitule": action, "identifiant": "123456"}]
    
    # Recherche des compétences
    resultat = search_competence(token, competences)
    
    if resultat:
        print("Résultat de la recherche :", resultat)
    else:
        print("Échec de la recherche des compétences.")

if __name__ == "__main__":
    main()
