import discord
import logging
import json
from discord.ext import commands
from discord.ext.commands import HelpCommand
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# --- Partie HelpCommand ---

class Commande_Aide(HelpCommand):
    def command_not_found(self, string):
        return f"Aucune commande nommée {string} n'a été trouvée."

    def get_command_signature(self, command):
        return f"{self.context.prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Manuel du Bot", color=0x00ff00)

        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in sorted(commands, key=lambda x: x.name)]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Commandes")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot = commands.Bot(command_prefix='!', intents=intents, help_command=Commande_Aide())

@bot.event
async def on_ready():
    print(f'Connecté sur le bot : {bot.user.name} avec son n° identifiant : {bot.user.id}')
    print('------')

# --- Partie Commandes Disponibles ---

@bot.command(name='commandes')
async def afficher_commandes(ctx):
    # Tri des commandes par nom
    command_list = [f'`{command.name}`' for command in sorted(bot.commands, key=lambda x: x.name)]
    commands_str = ', '.join(command_list)
    await ctx.send(f'Commandes disponibles : {commands_str}')

# --- Partie Erreurs Commandes ---

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Commande non valide. Utilisez `{ctx.prefix}afficher_commandes` pour voir les commandes disponibles.")

# --- Partie Présentation du bot ---

@bot.command(name='presentation')
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
@bot.command(name='nouveautes')
async def fct_nouveautes(ctx):
    embed = discord.Embed(
        title="Changements effectuées",
        description="Découvrez les dernières nouveautés et mises à jour de notre bot !\n",
        color=0x3498db  # Couleur bleue
    )

    # Charger les informations depuis un fichier JSON
    try:
        with open('nouveautes_data.json', 'r') as file:
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
    with open('nouveautes_data.json', 'r') as file:
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
    with open('nouveautes_data.json', 'w') as file:
        json.dump(anciennes_donnees, file, indent=4)
else:
    # Ajouter les nouvelles données aux anciennes données
    anciennes_donnees['versions'].append(donnees)

    # Sauvegarder les données mises à jour dans le fichier JSON
    with open('nouveautes_data.json', 'w') as file:
        json.dump(anciennes_donnees, file, indent=4)


# --- Partie Annonces ---

def chargements_annonces():
    try:
        with open('annonces.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"annonces": {}, "annonce_id_counter": 1}

def sauvegarder_annonces(annonces_data):
    with open('annonces.json', 'w') as file:
        json.dump(annonces_data, file, indent=2)

@bot.command(name='ajouter_annonce')
async def ajouter_annonce(ctx, canal: str = None, *, message: str = None):
    annonces_data = chargements_annonces()
    annonces = annonces_data["annonces"]
    annonce_id_counter = annonces_data["annonce_id_counter"]

    if isinstance(ctx.author, discord.Member):
        # Vérifier si le nom ou l'ID du canal est spécifié
        if canal is None:
            await ctx.send("Veuillez spécifier le nom ou l'ID du canal et le message que vous souhaitez annoncer.")
            return

        found_channel = None
        # Vérifiez si le canal est un numéro d'identifiant
        if canal.isdigit():
            found_channel = ctx.guild.get_channel(int(canal))
        else:
            # Recherchez le canal par nom
            for channel in ctx.guild.text_channels:
                if canal.lower() in channel.name.lower():
                    found_channel = channel
                    break

        # Vérifier si le canal existe
        if found_channel is None:
            await ctx.send(f'Aucun canal "{canal}" n\'a été trouvé sur le serveur.')
            return

        # Vérifier si le message est spécifié
        if message is None:
            await ctx.send("Veuillez spécifier le message que vous souhaitez annoncer.")
            return

        annonce_id = annonce_id_counter
        annonce_id_counter += 1

        # Stockez l'annonce dans le dictionnaire
        annonces[annonce_id] = {
            "channel_id": found_channel.id,
            "message": message,
            "message_preview": message[:50]
        }

        # Envoyer le message dans le canal spécifié
        sent_message = await found_channel.send(f"{message}")
        annonces[annonce_id]["message_id"] = sent_message.id  # Enregistrez l'ID du message

        # Mettez à jour le compteur d'annonce_id dans le fichier
        annonces_data["annonce_id_counter"] = annonce_id_counter
        sauvegarder_annonces(annonces_data)

        await ctx.send(f'L\'annonce n°{annonce_id} ajoutée avec succès sur le canal #{found_channel.name} !')

@bot.command(name='modifier_annonce')
@commands.has_permissions(administrator=True)
async def modifier_annonce(ctx, annonce_id: int = None, new_message: str = None):
    annonces_data = chargements_annonces()
    annonces = annonces_data["annonces"]

    if isinstance(ctx.author, discord.Member):
        if "Admin" in [role.name for role in ctx.author.roles]:
            # Vérifier si l'ID de l'annonce est spécifié
            if annonce_id is None:
                await ctx.send("Veuillez spécifier l'ID de l'annonce que vous souhaitez modifier.")
                return

            str_annonce_id = str(annonce_id)  # Convertir l'ID en chaîne
            if str_annonce_id not in annonces:
                await ctx.send(f'Aucune annonce avec l\'ID {annonce_id} n\'a été trouvée.')
                return

            annonce = annonces[str_annonce_id]

            # Vérifier si le message est modifié
            if new_message is not None:
                annonce["message"] = new_message
                annonce["message_preview"] = new_message[:50]

            # Vérifier si le nouveau message est spécifié
            if new_message is None:
                await ctx.send("Veuillez spécifier le nouveau message que vous souhaitez définir.")
                return

            # Mettre à jour le message dans le canal existant
            try:
                sent_message = await bot.get_channel(annonce["channel_id"]).fetch_message(annonce["message_id"])
                if sent_message:
                    await sent_message.edit(content=f"{new_message}")
                    await ctx.send(f'L\'annonce n° {str_annonce_id} modifiée avec succès.')
                    sauvegarder_annonces(annonces_data)
                else:
                    await ctx.send(f'Impossible de trouver le message d\'annonce avec l\'ID {annonce["message_id"]}.')
            except discord.NotFound:
                await ctx.send(f'Impossible de trouver le message d\'annonce avec l\'ID {annonce["message_id"]}.')
        else:
            await ctx.send('Vous n\'avez pas les permissions nécessaires.')
    else:
        await ctx.send('Cette commande doit être exécutée sur un serveur, pas en message privé.')

@bot.command(name='supprimer_annonce')
@commands.has_permissions(administrator=True)
async def supprimer_annonce(ctx, annonce_id: int = None):
    annonces_data = chargements_annonces()
    annonces = annonces_data["annonces"]

    if isinstance(ctx.author, discord.Member):
        if "Admin" in [role.name for role in ctx.author.roles]:
            # Vérifier si l'ID de l'annonce est spécifié
            if annonce_id is None:
                await ctx.send("Veuillez spécifier l'ID de l'annonce que vous souhaitez supprimer.")
                return

            str_annonce_id = str(annonce_id)  # Convertir l'ID en chaîne
            if str_annonce_id not in annonces:
                await ctx.send(f'Aucune annonce avec l\'ID {annonce_id} n\'a été trouvée.')
                return

            annonce = annonces[str_annonce_id]

            # Supprimer l'annonce du dictionnaire
            del annonces[str_annonce_id]
            sauvegarder_annonces(annonces_data)

            # Supprimer le message dans le canal existant
            try:
                sent_message = await bot.get_channel(annonce["channel_id"]).fetch_message(annonce["message_id"])
                if sent_message:
                    await sent_message.delete()
                    await ctx.send(f'L\'annonce n° {str_annonce_id} a été supprimée avec succès.')
                else:
                    await ctx.send(f'Impossible de trouver le message d\'annonce avec l\'ID {annonce["message_id"]}.')
            except discord.NotFound:
                await ctx.send(f'Impossible de trouver le message d\'annonce avec l\'ID {annonce["message_id"]}.')
        else:
            await ctx.send('Vous n\'avez pas les permissions nécessaires.')
    else:
        await ctx.send('Cette commande doit être exécutée sur un serveur, pas en message privé.')

@bot.command(name='annonces')
@commands.has_permissions(administrator=True)
async def afficher_annonces(ctx):
    annonces_data = chargements_annonces()
    annonces = annonces_data["annonces"]

    # Vérifier si l'utilisateur a le rôle d'administrateur
    if "Admin" in [role.name for role in ctx.author.roles]:
        if annonces:
            annonces_info = []
            for annonce_id, annonce_data in annonces.items():
                channel_name = bot.get_channel(annonce_data["channel_id"]).name
                message_id = annonce_data["message_id"]
                message_preview = annonce_data["message_preview"]  # Afficher les 50 premiers caractères du message
                annonces_info.append(f"N° de l'annonce : {annonce_id} | Salon : {channel_name} | Message : {message_preview}")

            annonces_str = '\n'.join(annonces_info)
            await ctx.send(f'Liste des annonces :\n-------------------- \n{annonces_str}')
        else:
            await ctx.send('Aucune annonce n\'a été ajoutée.')
    else:
        await ctx.send('Vous n\'avez pas les permissions nécessaires.')


# --- Partie Tickets ---

# Charger les données des tickets depuis un fichier JSON
def charger_tickets():
    try:
        with open('tickets_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'tickets': []}

# Sauvegarder les données des tickets dans un fichier JSON
def sauvegarder_tickets(data):
    with open('tickets_data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Fonction pour ouvrir un nouveau ticket
def ouvrir_nouveau_ticket(data, auteur_id, auteur_nom, sujet, canal_id):
    ticket_id = len(data['tickets']) + 1
    nouveau_ticket = {
        'id': ticket_id,
        'canal_id': canal_id,
        'auteur_id': auteur_id,
        'auteur_nom': auteur_nom,
        'sujet': sujet,
        'heure_creation': str(datetime.now()),
        'heure_fermeture': None,
        'statut': 'ouvert'
    }
    data['tickets'].append(nouveau_ticket)
    sauvegarder_tickets(data)
    return ticket_id

# Fonction pour fermer un ticket
def fermer_ticket(data, ticket_id):
    for ticket in data['tickets']:
        if ticket['id'] == ticket_id and ticket['statut'] == 'ouvert':
            ticket['statut'] = 'fermer'
            ticket['heure_fermeture'] = str(datetime.now())
            sauvegarder_tickets(data)
            return ticket  # Ticket fermé avec succès
    return None  # Ticket non trouvé ou déjà fermé

# Fonction pour afficher la liste des tickets
def afficher_liste_tickets(data):
    tickets_ouverts = [ticket for ticket in data['tickets'] if ticket['statut'] == 'ouvert']
    tickets_fermes = [ticket for ticket in data['tickets'] if ticket['statut'] == 'fermer']
    return tickets_ouverts, tickets_fermes

def chercher_pseudo_auteur(guild, auteur_id):
    membre = guild.get_member(auteur_id)
    return membre.name if membre else "Membre introuvable"

def chercher_canal_ticket(guild, canal_id):
    for canal in guild.channels:
        if isinstance(canal, discord.TextChannel) and canal.id == canal_id:
            return canal.mention
    return "Canal non trouvé"

@bot.command(name='ouvrir_ticket')
async def ouvrir_ticket(ctx, *, sujet=None):
    # Charger les données des tickets
    tickets_data = charger_tickets()

    if ctx.author.id in [ticket['auteur_id'] for ticket in tickets_data['tickets'] if ticket['statut'] == 'ouvert']:
        await ctx.send("Vous avez déjà un ticket ouvert. Veuillez fermer le ticket existant avant d'en ouvrir un nouveau.")
        return
    
    if sujet is None:
        await ctx.send("Veuillez fournir un sujet pour le ticket.")
        return

    # Créer un canal privé pour le ticket
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    try:
        ticket_channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}', overwrites=overwrites)
    except discord.Forbidden:
        print("Le bot n'a pas les autorisations nécessaires pour créer un canal.")
        await ctx.send("Le bot n'a pas les autorisations nécessaires pour créer un canal de ticket.")
        return
    except Exception as e:
        print(f"Erreur lors de la création du canal de ticket : {e}")
        await ctx.send("Une erreur s'est produite lors de la création du ticket. Veuillez réessayer plus tard.")
        return

    # Mettre à jour les données des tickets
    ticket_id = ouvrir_nouveau_ticket(tickets_data, ctx.author.id, ctx.author.name, sujet, ticket_channel.id)

    # Envoyer un message d'accueil dans le canal du ticket
    try:
        await ticket_channel.send(f"Bienvenue dans votre ticket ! Sujet : {sujet}")
        print("Ticket ouvert - Sujet :", sujet, "- N° du canal :", ticket_channel.id)
    except discord.Forbidden:
        print("Le bot n'a pas les autorisations nécessaires pour envoyer des messages dans le canal.")
        await ctx.send("Le bot n'a pas les autorisations nécessaires pour envoyer des messages dans le canal de ticket.")
        return

    # Informer l'utilisateur que le ticket a été créé
    await ctx.send(f"Votre ticket a été ouvert avec succès ! Vous pouvez le trouver dans {ticket_channel.mention} avec le n° ID : {ticket_id}.")

@bot.command(name='fermer_ticket')
@commands.has_permissions(administrator=True)
async def fct_fermer_ticket(ctx, ticket_id: int = None):
    # Charger les données des tickets
    tickets_data = charger_tickets()

    if "Admin" in [role.name for role in ctx.author.roles]:
        if ticket_id is None:
            await ctx.send("Veuillez spécifier le n° ID du ticket que vous souhaitez fermer.")
            return

        ticket_ferme = fermer_ticket(tickets_data, ticket_id)

        if ticket_ferme:
            # Récupérer le canal du ticket
            ticket_channel = bot.get_channel(ticket_ferme['canal_id'])

            # Supprimer le canal du ticket
            if ticket_channel:
                await ticket_channel.delete()

            await ctx.send(f"Le ticket avec l'ID n°{ticket_id} a été fermé avec succès, et le canal a été supprimé.")
        else:
            await ctx.send(f"Impossible de trouver le ticket avec l'ID n°{ticket_id} ou il est déjà fermé.")
    else:
        await ctx.send("Vous n'avez pas les permissions nécessaires.")

@bot.command(name='tickets')
async def voir_tickets(ctx):
    # Charger les données des tickets
    tickets_data = charger_tickets()

    if "Admin" in [role.name for role in ctx.author.roles]:
        tickets_ouverts, tickets_fermes = afficher_liste_tickets(tickets_data)
        
        message_ouverts = "Tickets ouverts :\n" + "\n".join([f"N° ID : {ticket['id']} - Auteur : {chercher_pseudo_auteur(ctx.guild, ticket['auteur_id'])} - Sujet : {ticket['sujet']} - Canal : {chercher_canal_ticket(ctx.guild, ticket['canal_id'])}" for ticket in tickets_ouverts]) if tickets_ouverts else "Aucun ticket ouvert actuellement."
        message_fermes = "Tickets fermés :\n" + "\n".join([f"N° ID : {ticket['id']} - Auteur : {chercher_pseudo_auteur(ctx.guild, ticket['auteur_id'])} - Sujet : {ticket['sujet']}" for ticket in tickets_fermes]) if tickets_fermes else "Aucun ticket fermé."

        await ctx.send(f"{message_ouverts}\n\n{message_fermes}")
    else:
        if ctx.author.id in [ticket['auteur_id'] for ticket in tickets_data['tickets']]:
            ticket_id = next(ticket['id'] for ticket in tickets_data['tickets'] if ticket['auteur_id'] == ctx.author.id)
            await ctx.send(f"Vous avez un ticket ouvert avec l'ID : {ticket_id}.")
        else:
            await ctx.send("Vous n'avez actuellement aucun ticket ouvert.")


# --- Partie Configuration des logs ---

# Configuration des journaux
logging.basicConfig(filename='bot_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# ID du canal Discord où vous souhaitez envoyer les logs
log_channel_id = 1178676165041459291

# Fonction pour envoyer un message de log à Discord
async def send_logs_to_channel(log_message):
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        await log_channel.send(log_message)

# Commande pour afficher l'historique des logs
@bot.command(name='logs')
@commands.has_permissions(administrator=True)
async def get_logs(ctx):
    if "Admin" in [role.name for role in ctx.author.roles]:
        try:
            # Lire le contenu du fichier de logs
            with open('bot_logs.log', 'r') as file:
                logs_content = file.read()

            # Envoyer le contenu des logs dans le canal Discord
            await ctx.send(f"```\n{logs_content}\n```")

        except FileNotFoundError:
            await ctx.send("Aucun log trouvé.")
    else:
        await ctx.send('Vous n\'avez pas les permissions nécessaires.')


bot.run('MTE3ODM4NTExMTY2NjkzMzg5MQ.GCBXvS.c_onrPj3Ll9yhAauSJEN4TGY3QjDi5-gFtpc6g')