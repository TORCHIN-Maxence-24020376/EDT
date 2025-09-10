import requests
import os
from datetime import datetime, timedelta

# Dossier où enregistrer les emplois du temps
DATA_DIR = "./edt_data"
os.makedirs(DATA_DIR, exist_ok=True)

PROJECT_ID = 8
RESOURCES = {
    #Nom du groupe : ID du groupe
    "1G1A": "8385",
    "1G1B": "8386",
    "1G2A": "8387",
    "1G2B": "8388",
    "1G3A": "8389",
    "1G3B": "8390",
    "1G4A": "8391",
    "1G4B": "8392",
    "2GA1-1" : "8400",
    "2GA1-2" : "8401",
    "2GA2-1" : "8402",
    "2GA2-2" : "8403",
    "2GB-1" : "8404",
    "2GB-2" : "8405",
    "3A1-1" : "42526",
    "3A1-2" : "42527",
    "3A2-1" : "42528",
    "3A2-2" : "42529",
    "3B-1" : "42530",
    "3B-2" : "42531,",
    # Maintenant nous passons aux emplois du temps personnalisés
    "NEVOT": "72627",
    "NICOLAS": "105296",
    "NINA": "1362",
}

compteur = 0

# Définir la plage de dates (dimanche - samedi)
aujourdhui = datetime.today()
if aujourdhui.weekday() == 6:  # Dimanche
    dimanche = aujourdhui
else:
    dimanche = aujourdhui - timedelta(days=aujourdhui.weekday() + 1)  # Aller au dernier dimanche

aujourdhui = datetime.today()
annee_actuelle = aujourdhui.year

# Si on est après aout, on télécharge pour l'année scolaire suivante
if aujourdhui.month > 8:
    annee_debut = annee_actuelle
    annee_fin = annee_actuelle + 1
else:
    annee_debut = annee_actuelle - 1
    annee_fin = annee_actuelle

date_debut = f"{annee_debut}-09-01"  # 1er septembre
date_fin = f"{annee_fin}-08-30"  # 30 aout

BASE_URL = "https://ade-web-consult.univ-amu.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"

# Télécharger chaque emploi du temps
def telecharger_edt(group, resource_id, retries=2):
    url = f"{BASE_URL}?projectId={PROJECT_ID}&resources={resource_id}&calType=ical&firstDate={date_debut}&lastDate={date_fin}"
    file_path = os.path.join(DATA_DIR, f"{group}.ics")

    for tentative in range(retries):
        print(f"🔍 Téléchargement de l'EDT pour {group} (tentative {tentative+1}) depuis {url}")
        response = requests.get(url)

        if response.status_code == 200:
            content = response.content
            if content.startswith(b"BEGIN:VCALENDAR"):
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f"✅ {group}.ics téléchargé et vérifié avec succès !")
                return True
            else:
                print(f"⚠️ {group}.ics invalide (ne commence pas par BEGIN:VCALENDAR), nouvelle tentative...")
        else:
            print(f"❌ Erreur {response.status_code} pour {group}")

    print(f"⛔ Impossible d'obtenir un fichier valide pour {group} après {retries} tentatives.")
    return False

for group, resource_id in RESOURCES.items():
    if telecharger_edt(group, resource_id):
        compteur += 1

print("📁", compteur, "/", len(RESOURCES), " emplois du temps valides ont été téléchargés.")

import subprocess

subprocess.run(["git", "add", "edt_data/*.ics"])
subprocess.run(["git", "commit", "-m", "Mise à jour automatique des emplois du temps"])
subprocess.run(["git", "push", "origin", "main"])