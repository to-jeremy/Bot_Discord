import discord
import json
import os

# Obtenez le chemin vers le dossier actuel du script
dossier_script = os.path.dirname(os.path.abspath(__file__))

# Construisez le chemin vers annonces_data.json dans src/data
chemin_fichier_json = os.path.join(dossier_script, 'data', 'annonces_data.json')

# --- Partie Annonces ---

def chargements_annonces():
    try:
        with open(chemin_fichier_json, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"annonces": {}, "annonce_id_counter": 1}

def sauvegarder_annonces(annonces_data):
    with open(chemin_fichier_json, 'w') as file:
        json.dump(annonces_data, file, indent=2)


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
                sent_message = await ctx.bot.get_channel(annonce["channel_id"]).fetch_message(annonce["message_id"])
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
                sent_message = await ctx.bot.get_channel(annonce["channel_id"]).fetch_message(annonce["message_id"])
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

async def afficher_annonces(ctx):
    annonces_data = chargements_annonces()
    annonces = annonces_data["annonces"]

    # Vérifier si l'utilisateur a le rôle d'administrateur
    if "Admin" in [role.name for role in ctx.author.roles]:
        if annonces:
            annonces_info = []
            for annonce_id, annonce_data in annonces.items():
                channel_name = ctx.bot.get_channel(annonce_data["channel_id"]).name
                message_id = annonce_data["message_id"]
                message_preview = annonce_data["message_preview"]  # Afficher les 50 premiers caractères du message
                annonces_info.append(f"N° de l'annonce : {annonce_id} | Salon : {channel_name} | Message : {message_preview}")

            annonces_str = '\n'.join(annonces_info)
            await ctx.send(f'Liste des annonces :\n-------------------- \n{annonces_str}')
        else:
            await ctx.send('Aucune annonce n\'a été ajoutée.')
    else:
        await ctx.send('Vous n\'avez pas les permissions nécessaires.')