from flask import Flask, request, send_file
import folium
import os
from supabase import create_client, Client

# 🔹 Configuration Supabase
SUPABASE_URL = "https://mufpmucjikpyxfakpxut.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11ZnBtdWNqaWtweXhmYWtweHV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyOTU1NTUsImV4cCI6MjA1Mzg3MTU1NX0.hKnBGT-YL7AmVSiFnGhiiSHRTgxbYcoLjf6ddQnGn4I"  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

def get_ecoles(formation_id):
    """Récupère les écoles depuis la base de données Supabase pour un formation_id donné."""
    try:
        response = supabase.table("ecoles").select("*").eq("formation_id", formation_id).execute()

        # Vérification si une erreur est survenue
        if "error" in response and response["error"]:
            print("❌ Erreur Supabase :", response["error"])
            return []

        ecoles = response.data  # ✅ Correction ici

        # 🔍 Vérification en console
        print(f"✅ {len(ecoles)} écoles récupérées pour formation_id={formation_id} :", ecoles)

        return [
            {
                "nom": e["Lieu d'enseignement (ENS) libellé"],
                "lat": e["ENS latitude"],
                "lon": e["ENS longitude"],
                "adresse": e["ENS adresse"]
            }
            for e in ecoles if e["ENS latitude"] and e["ENS longitude"]
        ]
    except Exception as e:
        print("❌ Erreur lors de la récupération des écoles:", e)
        return []

@app.route("/generate_map")
def generate_map():
    """Génère la carte avec les écoles associées à un formation_id et la sauvegarde en HTML."""
    formation_id = request.args.get("formation_id")

    if not formation_id:
        return "❌ Erreur : formation_id manquant."

    ecoles = get_ecoles(formation_id)
    
    if not ecoles:
        return "❌ Aucune école trouvée pour cette formation."

    # Définition du centre de la carte (première école par défaut)
    center = [float(ecoles[0]["lat"]), float(ecoles[0]["lon"])]

    # Création de la carte avec Folium
    m = folium.Map(location=center, zoom_start=6)

    # Ajouter chaque école comme marqueur
    for ecole in ecoles:
        folium.Marker(
            location=[float(ecole["lat"]), float(ecole["lon"])],
            popup=f"<b>{ecole['nom']}</b><br>{ecole['adresse']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Sauvegarde de la carte en HTML
    map_path = "map.html"
    m.save(map_path)
    
    return send_file(map_path)  # Retourne le fichier HTML pour l'affichage

if __name__ == "__main__":
    app.run(debug=True, port=5001)
