import discord
import json
import os

# Obtenez le chemin vers le dossier actuel du script
dossier_script = os.path.dirname(os.path.abspath(__file__))

# Construisez le chemin vers nouveautes_data.json dans src/data
chemin_fichier_json = os.path.join(dossier_script, 'data', 'nouveautes_data.json')

# --- Partie Présentation du bot ---

async def presentation(ctx):
    embed = discord.Embed(
        title="Présentation du Bot",
        description="Je suis un bot Discord en cours de développement donc je suis hébergé localement par mon créateur ! Pour le moment, je suis en phase des tests.",
        color=0x3498db  # Couleur bleue
        #color=0xff0000  # Couleur rouge
    )

    embed.add_field(
        name="Fonctionnalités principales",
        value="1. Annonces\n2. Tickets\n3. Manuel de commandes\n4. Présentation nouveautés et mises à jours",
        inline=False
    )

    embed.add_field(
        name="Commandes",
        value="Utilisez `!help` ou `!afficher_commandes` pour afficher la liste des commandes disponibles.",
        inline=False
    )

    embed.set_footer(text="*Le Serviteur*")

    await ctx.send(embed=embed)


# --- Partie Présentations changements sur le bot ---

# Définition de la fonction pour mettre à jour les informations
def mettre_a_jour_nouveautes(embed, version_data):
    version = version_data.get("version", "")
    nouveautes = version_data.get("nouveautes", [])
    mises_a_jour = version_data.get("mises_a_jour", [])

    embed.add_field(
        name=f"V{version}",
        value="",
        inline=False
    )

    # Section Nouveautés
    embed.add_field(
        name="Nouveautés",
        value="\n".join(nouveautes),
        inline=False
    )

    # Section Mises à Jour
    embed.add_field(
        name="Mises à Jour",
        value="\n".join(mises_a_jour),
        inline=False
    )

    embed.set_footer(text="Merci beaucoup !")

# Définition de la commande nouveautes
async def fct_nouveautes(ctx):
    embed = discord.Embed(
        title="Changements effectuées",
        description="Découvrez les dernières nouveautés et mises à jour de notre bot !\n",
        color=0x3498db  # Couleur bleue
    )

    # Charger les informations depuis un fichier JSON
    try:
        with open(chemin_fichier_json, 'r') as file:
            data = json.load(file)
            versions = data.get("versions", [])
            if versions:
                # Afficher uniquement la dernière version
                derniere_version = versions[-1]
                mettre_a_jour_nouveautes(embed, derniere_version)
    except FileNotFoundError:
        print("Le fichier 'nouveautes_data.json' n'a pas été trouvé.")
        return
    except json.JSONDecodeError as e:
        print(f"Erreur lors du décodage JSON : {e}")
        return

    await ctx.send(embed=embed)

# Sauvegarde des données dans un fichier
nouveautes = [
    "Changements de méthode pour le stockage des données \n--> Création d'un fichier JSON",
]

mises_a_jour = [
    "Modifications pour la prise en compte des nouvelles informations de la version actuelle",
]

donnees = {
    'version': '1.1.1 (29/11/2023)',
    'nouveautes': nouveautes,
    'mises_a_jour': mises_a_jour
}

# Charger les anciennes données depuis le fichier JSON
try:
    with open(chemin_fichier_json, 'r') as file:
        anciennes_donnees = json.load(file)
except FileNotFoundError:
    # Si le fichier n'existe pas, initialisez les données comme un dictionnaire vide ou une structure appropriée
    anciennes_donnees = {'versions': []}

# Vérifier si la version actuelle est déjà présente dans les données
version_actuelle = donnees['version']
versions_existantes = [v.get('version') for v in anciennes_donnees['versions']]

if version_actuelle in versions_existantes:
    # Mettre à jour les informations pour la version actuelle
    for version_data in anciennes_donnees['versions']:
        if version_data.get('version') == version_actuelle:
            version_data.update(donnees)

    # Sauvegarder les données mises à jour dans le fichier JSON
    with open(chemin_fichier_json, 'w') as file:
        json.dump(anciennes_donnees, file, indent=4)
else:
    # Ajouter les nouvelles données aux anciennes données
    anciennes_donnees['versions'].append(donnees)

    # Sauvegarder les données mises à jour dans le fichier JSON
    with open(chemin_fichier_json, 'w') as file:
        json.dump(anciennes_donnees, file, indent=4)
