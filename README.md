# README — Téléchargement automatique des emplois du temps (ADE → ICS → Git)

## Règles

* Script Python qui télécharge des emplois du temps **ADE** au format **ICS** pour une liste de groupes, puis **commit & push** les fichiers dans un dépôt **Git**.
* Fenêtre temporelle de l’année scolaire : du **1er septembre** (année N) au **30 juin** (année N+1).
* Fichiers ICS enregistrés dans `./edt_data/` (créé si besoin).
* Chaque groupe est identifié par une **ressource ADE** (ID numérique) dans `RESOURCES`.
* Sortie console : logs de téléchargement (succès/erreur) + comptage final.
* Git est invoqué via `subprocess` pour `add` / `commit` / `push`.

## Étapes

1. **Préparer l’environnement**

   * Installer Python 3.x et `pip`.
   * Installer la dépendance :

     ```bash
     pip install requests
     ```
   * Initialiser/configurer Git (dépôt déjà cloné, branch `main`, remote `origin` configuré et authentifié).

2. **Configurer le script**

   * Vérifier/adapter :

     * `DATA_DIR` : dossier de sortie (`./edt_data`).
     * `PROJECT_ID` : ID de projet ADE (ici `8`).
     * `RESOURCES` : mapping `NomGroupe → ID`.
       **Attention** : corriger `"3B-2": "42531,"` → `"3B-2": "42531"` (la virgule finale dans la chaîne casse l’URL).
   * Les dates sont calculées automatiquement selon le mois courant :

     * Si **après juin** → fenêtre `[1er septembre (année courante) → 30 juin (année suivante)]`.
     * Sinon → fenêtre `[1er septembre (année précédente) → 30 juin (année courante)]`.

3. **Exécuter**

   * Lancer :

     ```bash
     python fetch_edt.py
     ```
   * Le script :

     1. Crée `edt_data/` si absent.
     2. Construit pour chaque groupe une URL ADE `anonymous_cal.jsp` avec `projectId`, `resources`, `firstDate`, `lastDate`.
     3. Télécharge le `.ics` (statut HTTP 200 attendu) et sauvegarde sous `edt_data/<GROUPE>.ics`.
     4. Compte les succès et affiche un récapitulatif.
     5. Exécute `git add`, `git commit`, puis `git push`.

4. **Vérifier**

   * Contrôler la console (statuts HTTP, compteur).
   * Vérifier que les `.ics` sont présents dans `edt_data/`.
   * Vérifier le commit distant (sur la plateforme Git).

## Sortie attendue

* **Fichiers** : un `.ics` par groupe dans `./edt_data/`.
* **Logs** (exemple) :

  ```
  🔍 Téléchargement de l'EDT pour 1G1A depuis https://ade-web-consult...&resources=8385&calType=ical&firstDate=2025-09-01&lastDate=2026-06-30
  ✅ 1G1A.ics téléchargé avec succès !
  ...
  📁 19 / 20  emplois du temps ont été téléchargés.
  ```
* **Git** : un commit intitulé “Mise à jour automatique des emplois du temps” poussé sur `main`.

## Prérequis

* **Python** : 3.8+ recommandé.
* **Paquets** : `requests`.
* **Accès réseau** : vers `https://ade-web-consult.univ-amu.fr/...`.
* **Git** : dépôt initialisé, remote `origin` configuré, droits de push.

## Paramètres clés

| Paramètre    | Type             | Rôle                      | Exemple                 |
| ------------ | ---------------- | ------------------------- | ----------------------- |
| `DATA_DIR`   | str              | Dossier de sortie des ICS | `./edt_data`            |
| `PROJECT_ID` | int              | Identifiant du projet ADE | `8`                     |
| `RESOURCES`  | dict\[str,str]   | Mapping groupe → ID ADE   | `"1G1A": "8385"`        |
| `date_debut` | str (YYYY-MM-DD) | Début fenêtre scolaire    | `2025-09-01`            |
| `date_fin`   | str (YYYY-MM-DD) | Fin fenêtre scolaire      | `2026-06-30`            |
| `BASE_URL`   | str              | Endpoint ADE ICS          | `.../anonymous_cal.jsp` |

## Détails du fonctionnement

* **Fenêtre temporelle**
  Le script calcule `annee_debut` / `annee_fin` selon le mois courant, puis formate `date_debut = "YYYY-09-01"` et `date_fin = "YYYY-06-30"`.

* **Construction des URLs**
  Pour chaque `(groupe, resource_id)` :
  `BASE_URL?projectId=...&resources=<ID>&calType=ical&firstDate=<date_debut>&lastDate=<date_fin>`

* **Téléchargement & écriture**
  `requests.get(url)` → si `status_code == 200`, écrire binaire dans `edt_data/<groupe>.ics`.

* **Journalisation & compteur**
  Affichage d’une ligne par groupe (succès/erreur), puis résumé `compteur / len(RESOURCES)`.

* **Intégration Git**
  Appels `subprocess.run` pour `git add`, `git commit`, `git push`.

## Exemple d’exécution (console)

```
🔍 Téléchargement de l'EDT pour 2GA1-1 depuis https://ade-web-consult...&resources=8400&calType=ical&firstDate=2025-09-01&lastDate=2026-06-30
✅ 2GA1-1.ics téléchargé avec succès !
❌ Erreur 404 pour 3A2-2
📁 18 / 20  emplois du temps ont été téléchargés.
[git] Ajout, commit, push…
```

## Dépannage

* **IDs de ressources** invalides → vérifier `RESOURCES` (ex. retirer la virgule dans `"42531,"`).
* **HTTP 4xx/5xx** → l’URL, les dates ou le service ADE peuvent être en cause.
* **`git add edt_data/*.ics` n’ajoute rien**
  En `subprocess.run([...])`, le joker `*` n’est **pas** expansé. Solutions :

  * Utiliser `glob` en Python pour lister les fichiers puis les passer à `git add`.
  * Ou appeler le shell : `subprocess.run("git add edt_data/*.ics", shell=True)`.
* **Échec du `push`** → vérifier l’authentification (SSH/HTTPS), la branche cible, les droits.
* **`requests` manquant** → `pip install requests`.
* **Dossier non versionné** → initialiser le dépôt (`git init`), ajouter `remote origin`, créer `main`.

## Bonnes pratiques

* Ajouter **timeouts** et **retries** sur `requests.get` (robustesse réseau).
* Valider les **IDs** et dédupliquer `RESOURCES`.
* Journaliser dans un **fichier log** (suivi des execs).
* Vérifier la présence d’un **`.gitignore`** adapté (si besoin).

## Améliorations possibles

* Paramétrer groupes et dates via **arguments CLI** (`argparse`).
* Exporter un **rapport** (CSV/JSON) listant les groupes téléchargés/échoués.
* Intégrer une **vérification de diff** (télécharger seulement si l’ICS change).
* Planifier l’exécution (cron/Task Scheduler) pour des mises à jour régulières.
