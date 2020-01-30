import logging
import random
import string

import Config
import cloudscraper
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

scraper = cloudscraper.create_scraper()

cogs = ["Verification", "Roles"]

bot = commands.Bot(command_prefix="v!", case_insensitive=True)
bot.remove_command("help")

for cog in cogs:
    bot.load_extension("Cogs." + cog)

logging.basicConfig(level=logging.INFO, format="Verification [%(levelname)s] | %(message)s")


def dev(ctx):
    return int(ctx.author.id) in Config.DEVIDS


@bot.command()
@commands.check(dev)
async def restart(ctx):
    """
    Restart the cogs.
    """
    restarting = discord.Embed(
        title="Restarting...",
        color=Config.MAINCOLOR
    )
    msg = await ctx.send(embed=restarting)
    for cog in cogs:
        bot.reload_extension("Cogs." + cog)
        restarting.add_field(name=f"{cog}", value="✅ Restarted!")
        await msg.edit(embed=restarting)
    restarting.title = "Bot Restarted"
    await msg.edit(embed=restarting)
    logging.info(
        f"Bot has been restarted successfully in {len(bot.guilds)} server(s) with {len(bot.users)} users by {ctx.author.name}#{ctx.author.discriminator} (ID - {ctx.author.id})!")
    await msg.delete(delay=3)
    if ctx.guild is not None:
        await ctx.message.delete(delay=3)


def randomString(stringLength=25):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


@bot.event
async def on_ready():
    logging.info(f"Bot has started successfully in {len(bot.guilds)} server(s) with {len(bot.users)} users!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="You"))


@bot.event
async def on_member_join(member):
    doc = Config.USERS.find_one({"user_id": member.id})
    if doc is not None:
        if doc['verified']:
            print("Verified Member Joined, Giving them Role")
            role = discord.utils.get(member.guild.roles, id=int(Config.VerifiedRoleID))
            await member.add_roles(role)
            buyurl = scraper.get(Config.BuyerPageURL + str(doc['Spigot ID']))  # Checks if user has purchased product
            buypage = BeautifulSoup(buyurl.content, "html.parser")
            current_name = buypage.find('h3').text  # Loads User's Current Username
            saved_name = doc['user_name']
            # Checks if User has changed username since Verification
            if current_name != saved_name:
                Config.USERS.update_one({"user_id": member.id},
                                        {"$set": {'user_name': current_name}})  # Updates username in MongoDB
                print(f"Updating {saved_name} to {current_name}")
            res = requests.get(Config.BuyerPageURL + "api/checkbuyer/?username=" + doc['user_name'])
            data = res.json()  # turns data into a JSON using requests
            print("Got JSON File")
            index = 0
            teardown = data["bought"]  # removes first part of json
            if teardown:  # IDK why but it checks if user purchased stuff.... Ya never know.
                for item in teardown:
                    itemdoc = Config.PLUGINS.find_one({'id': int(teardown[index]["id"])})
                    if itemdoc is not None:
                        role = discord.utils.get(member.guild.roles, id=int(itemdoc['roleid']))
                        if role is not None:
                            await member.add_roles(role)
                    index += 1


bot.run(Config.TOKEN)
