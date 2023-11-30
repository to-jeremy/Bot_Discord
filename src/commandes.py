# commandes.py
import discord
from discord.ext import commands
from discord.ext.commands import HelpCommand

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

# --- Partie Commandes Disponibles ---

async def afficher_commandes(ctx):
    # Tri des commandes par nom
    command_list = [f'`{command.name}`' for command in sorted(ctx.bot.commands, key=lambda x: x.name)]
    commands_str = ', '.join(command_list)
    await ctx.send(f'Commandes disponibles : {commands_str}')
