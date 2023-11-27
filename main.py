import discord
from discord.ext import commands
from discord.ext.commands import HelpCommand

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class Commande_Aide(HelpCommand):
    def command_not_found(self, string):
        return f"Aucune commande nommée {string} n'a été trouvée."

    def get_command_signature(self, command):
        return f"{self.context.prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Commandes du Bot", color=0x00ff00)

        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in sorted(commands, key=lambda x: x.name)]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Autre")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot = commands.Bot(command_prefix='!', intents=intents, help_command=Commande_Aide())

@bot.event
async def on_ready():
    print(f'Connecté sur le bot : {bot.user.name} avec son n° identifiant : {bot.user.id}')
    print('------')

@bot.command(name='afficher_commandes')
async def afficher_commandes(ctx):
    # Tri des commandes par nom
    command_list = [f'`{command.name}`' for command in sorted(bot.commands, key=lambda x: x.name)]
    commands_str = ', '.join(command_list)
    await ctx.send(f'Commandes disponibles : {commands_str}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Commande non valide. Utilisez `{ctx.prefix}afficher_commandes` pour voir les commandes disponibles.")

annonces = {}  # Dictionnaire pour stocker les annonces avec leur ID comme clé
annonce_id_counter = 1

@bot.command(name='ajouter_annonce')
async def annonce(ctx, canal: str = None, *, message: str = None):
    global annonce_id_counter
    if isinstance(ctx.author, discord.Member):
        if "Admin" in [role.name for role in ctx.author.roles]:
            if canal is None and message is None:
                await ctx.send("Veuillez spécifier le nom ou l'ID du canal et le message que vous souhaitez annoncer.")
                return
            elif canal is not None and message is None:
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

                if found_channel is not None:
                    await ctx.send("Veuillez spécifier le message que vous souhaitez annoncer.")
                else:
                    await ctx.send(f'Aucun canal "{canal}" n\'a été trouvé sur le serveur.')
                return

            found_channel = None
            # Vérifiez si le canal est un numéro d'identifiant
            if canal.isdigit():
                found_channel = ctx.guild.get_channel(int(canal))
            else:
                # Recherchez le canal par nom
                for channel in ctx.guild.text_channels:
                    if canal is not None and canal.lower() in channel.name.lower():
                        found_channel = channel
                        break

            if found_channel is not None:
                annonce_id = annonce_id_counter
                annonce_id_counter += 1

                # Stockez l'annonce dans le dictionnaire
                annonces[annonce_id] = {"channel": found_channel, "message": message}

                await found_channel.send(f"{message}")
                print(f'Annonce n°{annonce_id} envoyée avec succès sur le canal #{found_channel.name} !')
            else:
                if canal is not None:
                    await ctx.send(f'Aucun canal "{canal}" trouvé sur le serveur.')
                else:
                    await ctx.send("Veuillez spécifier le nom ou l'ID du canal sur lequel vous souhaitez envoyer l'annonce.")
        else:
            await ctx.send('Vous n\'avez pas les permissions nécessaires.')
    else:
        await ctx.send('Cette commande doit être exécutée sur un serveur, pas en message privé.')


@bot.command(name='afficher_annonces')
async def afficher_annonces(ctx):
    # Vérifier si l'utilisateur a le rôle d'administrateur
    if "Admin" in [role.name for role in ctx.author.roles]:
        if annonces:
            annonces_info = []
            for annonce_id, annonce_data in annonces.items():
                channel_name = annonce_data["channel"].name
                message_preview = annonce_data["message"][:50]  # Afficher les 50 premiers caractères du message
                annonces_info.append(f"N° ID : {annonce_id} | Salon : {channel_name} | Message : {message_preview}")

            annonces_str = '\n'.join(annonces_info)
            await ctx.send(f'Liste des annonces :\n-------------------- \n{annonces_str}')
        else:
            await ctx.send('Aucune annonce n\'a été ajoutée.')
    else:
        await ctx.send('Vous n\'avez pas les permissions nécessaires.')


tickets_ouverts = {}

@bot.command(name='ouvrir_ticket')
async def ouvrir_ticket(ctx, *, sujet=None):
    # Vérifie si l'utilisateur a déjà un ticket ouvert
    if ctx.author.id in tickets_ouverts:
        await ctx.send("Vous avez déjà un ticket ouvert. Veuillez fermer le ticket existant avant d'en ouvrir un nouveau.")
        return
    
    # Validation du sujet (vous pouvez personnaliser cette vérification)
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

    # Stocker le canal du ticket dans le dictionnaire
    tickets_ouverts[ctx.author.id] = (ticket_channel.id, sujet)

    # Envoyer un message d'accueil dans le canal du ticket
    try:
        await ticket_channel.send(f"Bienvenue dans votre ticket ! Sujet : {sujet}")
        print("Ticket ouvert - Sujet :", sujet, "- N° du canal :", ticket_channel.id)
    except discord.Forbidden:
        print("Le bot n'a pas les autorisations nécessaires pour envoyer des messages dans le canal.")
        await ctx.send("Le bot n'a pas les autorisations nécessaires pour envoyer des messages dans le canal de ticket.")
        return

    # Informer l'utilisateur que le ticket a été créé
    await ctx.send(f"Votre ticket a été ouvert avec succès ! Vous pouvez le trouver dans {ticket_channel.mention}.")
    print("Information du canal créé pour l'utilisateur faite")


@bot.command(name='fermer_ticket')
@commands.has_permissions(administrator=True)
async def fermer_ticket(ctx, ticket_id: int = None):
    # Si aucun ticket_id n'est fourni
    if ticket_id is None:
        await ctx.send("Veuillez spécifier l'ID du ticket que vous souhaitez fermer.")
        return

    # Appeler la fonction pour fermer un ticket spécifique
    await fermer_ticket_specifique(ctx, ticket_id)

# Fonction pour fermer un ticket spécifique
async def fermer_ticket_specifique(ctx, ticket_id: int):
    # Vérifie si le ticket_id existe dans le dictionnaire
    if ticket_id not in {v[0] for v in tickets_ouverts.values()}:
        await ctx.send(f"Ticket avec l'ID n°{ticket_id} non trouvé.")
        return

    # Trouver l'utilisateur associé à ce ticket_id
    user_id = None
    sujet_ticket = None
    for uid, (tid, sujet) in tickets_ouverts.items():
        if tid == ticket_id:
            user_id = uid
            sujet_ticket = sujet
            break

    # Récupérer le canal du ticket
    ticket_channel = bot.get_channel(ticket_id)

    # Supprimer le canal du ticket
    await ticket_channel.delete()

    # Retirer l'utilisateur du dictionnaire des tickets ouverts
    if user_id:
        del tickets_ouverts[user_id]

    # Informer l'administrateur que le ticket a été fermé avec le nom du sujet
    await ctx.send(f"Le ticket avec l'ID n°{ticket_id} (Sujet : {sujet_ticket}) a été fermé avec succès.")


@bot.command(name='tickets')
async def voir_tickets(ctx):
    # Vérifie si l'auteur de la commande est un administrateur
    if ctx.author.guild_permissions.administrator:
        # Affiche la liste des tickets ouverts avec leurs ID et le nom du sujet
        tickets_info = [f"Ticket : {ticket_id} - Sujet : {ticket_sujet}" 
                        for (ticket_id, ticket_sujet) in tickets_ouverts.values()]
        message = "\n".join(tickets_info)

        if message:
            await ctx.send(f"Tickets ouverts :\n ---------------- \n{message}")
        else:
            await ctx.send("Aucun ticket ouvert actuellement.")
    else:
        # Si l'auteur n'est pas administrateur, vérifie s'il a un ticket ouvert
        if ctx.author.id in tickets_ouverts:
            ticket_id, ticket_sujet = tickets_ouverts[ctx.author.id]
            await ctx.send(f"Vous avez un ticket ouvert - Sujet : {ticket_sujet} - Numéro du ticket : {ticket_id}")
        else:
            await ctx.send("Vous n'avez actuellement aucun ticket ouvert.")


bot.run('MTE3ODM4NTExMTY2NjkzMzg5MQ.GCBXvS.c_onrPj3Ll9yhAauSJEN4TGY3QjDi5-gFtpc6g')