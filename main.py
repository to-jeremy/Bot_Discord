# main.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.commandes import Commande_Aide, afficher_commandes
from src.presentation import presentation, fct_nouveautes
from src.annonces import afficher_annonces, ajouter_annonce, modifier_annonce, supprimer_annonce
#from src.tickets import ouvrir_ticket, fct_fermer_ticket, voir_tickets
#from src.logs import get_logs

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

token = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents=intents, help_command=Commande_Aide())

@bot.event
async def on_ready():
    print(f'Connecté sur le bot : {bot.user.name} avec son n° identifiant : {bot.user.id}')
    print('------')

# --- Partie Erreurs Commandes ---

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Commande non valide. Utilisez `{ctx.prefix}afficher_commandes` pour voir les commandes disponibles.")

# --- Partie Commandes Disponibles ---

@bot.command(name='commandes')
async def cmd_afficher_commandes(ctx):
    await afficher_commandes(ctx)

# --- Partie Présentation du bot ---

@bot.command(name='presentation')
async def cmd_presentation(ctx):
    await presentation(ctx)

@bot.command(name='nouveautes')
async def cmd_nouveautes(ctx):
    await fct_nouveautes(ctx)

# --- Partie Annonces ---

@bot.command(name='ajouter_annonce')
async def cmd_ajouter_annonce(ctx, canal: str = None, *, message: str = None):
    await ajouter_annonce(ctx, canal = canal, message = message)

@bot.command(name='modifier_annonce')
@commands.has_permissions(administrator = True)
async def cmd_modifier_annonce(ctx, annonce_id: int = None, new_message: str = None):
    await modifier_annonce(ctx, annonce_id = annonce_id, new_message = new_message)

@bot.command(name='supprimer_annonce')
@commands.has_permissions(administrator=True)
async def cmd_supprimer_annonce(ctx, annonce_id: int = None):
    await supprimer_annonce(ctx, annonce_id = annonce_id)

@bot.command(name='annonces')
@commands.has_permissions(administrator=True)
async def cmd_afficher_annonces(ctx):
    await afficher_annonces(ctx)


if __name__ == "__main__":
    bot.run(token)
