import discord
import json
import os
from datetime import datetime

# Obtenez le chemin vers le dossier actuel du script
dossier_script = os.path.dirname(os.path.abspath(__file__))

# Construisez le chemin vers nouveautes_data.json dans src/data
chemin_fichier_json = os.path.join(dossier_script, 'data', 'tickets_data.json')

# --- Partie Tickets ---

# Charger les données des tickets depuis un fichier JSON
def charger_tickets():
    try:
        with open(chemin_fichier_json, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'tickets': []}

# Sauvegarder les données des tickets dans un fichier JSON
def sauvegarder_tickets(data):
    with open(chemin_fichier_json, 'w') as file:
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

async def chercher_pseudo_auteur(guild, auteur_id):
    try:
        # Charger les données des tickets depuis le fichier JSON
        tickets_data = charger_tickets()

        # Chercher l'auteur dans les données des tickets
        for ticket in tickets_data['tickets']:
            if ticket['auteur_id'] == auteur_id:
                return ticket['auteur_nom']

        # Si l'auteur n'est pas trouvé, renvoyer un message approprié
        return f"Membre introuvable (n° ID : {auteur_id})"
    except discord.NotFound:
        return f"Membre introuvable (n° ID : {auteur_id})"


def chercher_canal_ticket(guild, canal_id):
    for canal in guild.channels:
        if isinstance(canal, discord.TextChannel) and canal.id == canal_id:
            return canal.mention
    return "Canal non trouvé"


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
    await ctx.send(f"Votre ticket a été ouvert avec succès ! Vous pouvez le trouver dans {ticket_channel.mention} avec le n°{ticket_id}.")


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
            ticket_channel = ctx.bot.get_channel(ticket_ferme['canal_id'])

            # Supprimer le canal du ticket
            if ticket_channel:
                await ticket_channel.delete()

            await ctx.send(f"Le ticket avec le n°{ticket_id} a été fermé avec succès, et le canal a été supprimé.")
        else:
            await ctx.send(f"Impossible de trouver le ticket avec le n°{ticket_id} ou il est déjà fermé.")
    else:
        await ctx.send("Vous n'avez pas les permissions nécessaires.")


async def voir_tickets(ctx):
    # Charger les données des tickets
    tickets_data = charger_tickets()

    if "Admin" in [role.name for role in ctx.author.roles]:
        tickets_ouverts, tickets_fermes = afficher_liste_tickets(tickets_data)
        
        messages_ouverts = "Tickets ouverts :\n" + "\n".join([f"N° ID : {ticket['id']} - Auteur : {await chercher_pseudo_auteur(ctx.guild, ticket['auteur_id'])} - Sujet : {ticket['sujet']} - Canal : {chercher_canal_ticket(ctx.guild, ticket['canal_id'])}" for ticket in tickets_ouverts]) if tickets_ouverts else "Aucun ticket ouvert actuellement."
        messages_fermes = "Tickets fermés :\n" + "\n".join([f"N° ID : {ticket['id']} - Auteur : {await chercher_pseudo_auteur(ctx.guild, ticket['auteur_id'])} - Sujet : {ticket['sujet']}" for ticket in tickets_fermes]) if tickets_fermes else "Aucun ticket fermé."

        await ctx.send(f"{messages_ouverts}\n\n{messages_fermes}")
    else:
        if ctx.author.id in [ticket['auteur_id'] for ticket in tickets_data['tickets']]:
            ticket_id = next(ticket['id'] for ticket in tickets_data['tickets'] if ticket['auteur_id'] == ctx.author.id)
            await ctx.send(f"Vous avez un ticket ouvert avec le n°{ticket_id}.")
        else:
            await ctx.send("Vous n'avez actuellement aucun ticket ouvert.")