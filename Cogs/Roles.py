import datetime

import Config
import cloudscraper
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['role'])
    async def roles(self, ctx):
        if ctx.guild is None:
            embed = discord.Embed(
                title="ERROR",
                description="This command can only be used in a Server.",
                timestamp=datetime.datetime.utcnow(),
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        else:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(
                    title="Roles",
                    description="`v!role join <RoleName>` - To Join a Plugin Role.\n`v!role leave <RoleName>` - To leave a Plugin Role.\n`v!role list` - List all the Plugins",
                    color=Config.MAINCOLOR
                )
                await ctx.send(embed=embed)

    @roles.command()
    async def join(self, ctx, *, name: str = None):
        if ctx.guild is None:  # checks is sent in Server
            print("User Sent message Via DM")
            embed = discord.Embed(
                title="ERROR",
                description="This command can only be used in a Server.",
                timestamp=datetime.datetime.utcnow(),
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        else:
            print(f"Join command initiated by {ctx.author.name}")
            if name is None:
                embed = discord.Embed(
                    title="Role Join Error",
                    description="Please provide a plugin name!",
                    color=Config.ERRORCOLOR
                )
                await ctx.send(embed=embed)
            else:
                pluginFind = Config.PLUGINS.find_one({"name": name.lower()})  # looks for plugin in names
                if pluginFind is not None:  # If plugin exists
                    pluginID = pluginFind['id']
                    doc = Config.USERS.find_one({"user_id": ctx.author.id})
                    if doc is None or doc['verified'] is False:
                        embed = discord.Embed(
                            title="Role Join Error",
                            description="You are Not Verified! Please use v!verify to continue!",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                    else:
                        print("Scraping Buyer Page")
                        scraper = cloudscraper.create_scraper()
                        buyurl = scraper.get(
                            Config.BuyerPageURL + str(doc['Spigot ID']))  # Checks if user has purchased product
                        print("Grabbed Buyer Page")
                        buypage = BeautifulSoup(buyurl.content, "html.parser")
                        print("Parsed HTML")
                        if buypage.find_all('div', attrs={
                            "class": "alert alert-danger tool-msg"}):  # If False, user has not purchased a product.
                            print("User didn't buy :(")
                            embed = discord.Embed(
                                title="No Purchase Found",
                                description="You have not purchased any product from this store.",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                        else:
                            current_name = buypage.find('h3').text  # Loads User's Current Username
                            saved_name = doc['user_name']
                            # Checks if User has changed username since Verification
                            if current_name != saved_name:
                                Config.USERS.update_one({"user_id": ctx.author.id}, {
                                    "$set": {'user_name': current_name}})  # Updates username in MongoDB
                                print(f"Updating {saved_name} to {current_name}")
                            res = requests.get(Config.BuyerPageURL + "api/checkbuyer/?username=" + doc['user_name'])
                            data = res.json()  # turns data into a JSON using requests
                            print("Got JSON File")

                            boughtCheck = False
                            index = 0
                            teardown = data["bought"]  # removes first part of json
                            for item in teardown:
                                print(f"Comparing IDs Index Of: {index}")
                                if str(teardown[index]["id"]) == str(pluginID):  # Compares IDs
                                    boughtCheck = True  # User has bought the plugin
                                index += 1
                            if boughtCheck:
                                role = discord.utils.get(ctx.guild.roles,
                                                         id=int(pluginFind['roleid']))  # Defines which role
                                print("Got role for Plugin")
                                await ctx.author.add_roles(role)
                                embed = discord.Embed(
                                    title="Success!",
                                    description="You have been added to the " + name + " plugin role!",  # prints it
                                    color=Config.MAINCOLOR
                                )
                                await ctx.send(embed=embed)
                            else:
                                embed = discord.Embed(
                                    title="Plugin not purchased",
                                    description="You have not purchased this Plugin",
                                    color=Config.MAINCOLOR
                                )
                                await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Not a Valid Plugin",
                        description="That is not a valid plugins, Use `v!role list` To a get a list of plugins",
                        color=Config.MAINCOLOR
                    )
                    await ctx.send(embed=embed)

    @roles.command()
    async def list(self, ctx):
        if ctx.guild is None:  # Checks if user sent in Server or not
            embed = discord.Embed(
                title="ERROR",
                description="This command can only be used in a Server.",
                timestamp=datetime.datetime.utcnow(),
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        else:
            all_docs = Config.PLUGINS.find({})
            str = "Current Plugins:\n\n"
            for item in all_docs:
                str += f"[{item['name']}](https://spigotmc.org/resources/{item['id']})\n"  # lists all the plugins
            embed = discord.Embed(
                title="Plugins",
                description=str,  # prints it
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)

    @roles.command()
    async def leave(self, ctx, *, name: str = None):
        if ctx.guild is None:  # user has sent message in DM
            embed = discord.Embed(
                title="ERROR",
                description="This command can only be used in a Server.",
                timestamp=datetime.datetime.utcnow(),
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        else:  # use has not sent command in DM
            if name is None:
                embed = discord.Embed(
                    title="Role Join Error",
                    description="Please provide a plugin name!",
                    color=Config.ERRORCOLOR
                )
                await ctx.send(embed=embed)
            else:  # user gave a role name
                pluginFind = Config.PLUGINS.find_one({"name": name.lower()})
                if pluginFind is not None:
                    doc = Config.USERS.find_one({"user_id": ctx.author.id})
                    if doc is None or doc['verified'] is False:  # user is not defined
                        embed = discord.Embed(
                            title="Role Leave Error",
                            description="You are Not Verified! Please use v!verify to continue!",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                    else:  # User is verified
                        role = discord.utils.get(ctx.guild.roles, id=int(pluginFind['roleid']))
                        if role in ctx.author.roles:
                            await ctx.author.remove_roles(role)  # removes the role
                            embed = discord.Embed(
                                title="Role Remove",
                                description=f"You have been removed from the {pluginFind['name']} role!",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title="Role Remove",
                                description="You do not have that role",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Role Error",
                        description="That plugin does not exist",
                        color=Config.ERRORCOLOR
                    )
                    await ctx.send(embed=embed)

    @roles.command()
    async def add(self, ctx):
        if ctx.author.id in Config.DEVIDS:
            embed = discord.Embed(
                title="Role Addition",
                description="What is the name of the role?",
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)
            while True:
                msg = await self.bot.wait_for('message')
                if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    name = str(msg.content)
                    break
            embed = discord.Embed(
                title="Role Addition",
                description="What is the ID for the Plugin on Spigot?",
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)
            while True:
                msg = await self.bot.wait_for('message')
                if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    try:
                        ID = int(msg.content)
                        break
                    except:
                        embed = discord.Embed(
                            title="ERROR",
                            description="That is not a Valid ID",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                        continue
            embed = discord.Embed(
                title="Role Addition",
                description="What is the ID for the Discord Role?",
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)
            while True:
                msg = await self.bot.wait_for('message')
                if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    try:
                        CheckID = int(msg.content)
                        role = discord.utils.get(ctx.guild.roles, id=CheckID)
                        if role is None:
                            embed = discord.Embed(
                                title="ERROR",
                                description="That is not a Valid ID",
                                color=Config.ERRORCOLOR
                            )
                            await ctx.send(embed=embed)
                        else:
                            DiscordID = CheckID
                            break
                    except:
                        embed = discord.Embed(
                            title="ERROR",
                            description="That is not a Valid ID",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                        continue
            embed = discord.Embed(
                title="Role Addition",
                description=f"Is this Correct?\nRole Name: {name}\nPlugin ID: {ID}\nRole ID: {DiscordID}",
                color=Config.MAINCOLOR
            )
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("🚫")
            while True:
                reaction, reactor = await self.bot.wait_for("reaction_add")
                if reactor.id is ctx.author.id:
                    if reaction.emoji == "🚫":
                        embed = discord.Embed(
                            title="Role Cancelation",
                            description="Canceled Addition",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                        await msg.delete()
                        break
                    elif reaction.emoji == "✅":
                        Config.PLUGINS.insert_one({'name': name.lower(), 'id': ID, 'roleid': DiscordID})
                        embed = discord.Embed(
                            title="Role Confirmation",
                            description="Added Role to DB!",
                            color=Config.MAINCOLOR
                        )
                        await ctx.send(embed=embed)
                        await msg.delete()
                        break

        else:
            embed = discord.Embed(
                title="ERROR",
                description="You don't have enough perms for that",
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)

    @roles.command()
    async def delete(self, ctx):
        if ctx.author.id in Config.DEVIDS:
            embed = discord.Embed(
                title="Role Addition",
                description="What is the ID for the Plugin on Spigot?",
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)
            while True:
                msg = await self.bot.wait_for('message')
                if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                    try:
                        ID = int(msg.content)
                        break
                    except:
                        embed = discord.Embed(
                            title="ERROR",
                            description="That is not a Valid ID",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                        continue
            doc = Config.PLUGINS.find_one({'id': ID})
            if doc is None:
                embed = discord.Embed(
                    title="ERROR",
                    description="That Plugin Does not exist in the DB",
                    color=Config.MAINCOLOR
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Role Removal",
                    description=f"Are you sure you want to remove this role?\nName: {doc['name']}\nID: {ID}\nDiscord ID: {doc['roleid']}",
                    color=Config.MAINCOLOR
                )
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("✅")
                await msg.add_reaction("🚫")
                while True:
                    reaction, reactor = await self.bot.wait_for("reaction_add")
                    if reactor.id is ctx.author.id:
                        if reaction.emoji == "🚫":
                            embed = discord.Embed(
                                title="Role Removal",
                                description="Canceled Removal",
                                color=Config.ERRORCOLOR
                            )
                            await ctx.send(embed=embed)
                            await msg.delete()
                            break
                        elif reaction.emoji == "✅":
                            Config.PLUGINS.delete_one({'id': ID})
                            embed = discord.Embed(
                                title="Removal Confirmation",
                                description="Removed Role from DB!",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                            await msg.delete()
                            break

        else:
            embed = discord.Embed(
                title="ERROR",
                description="You don't have enough perms for that",
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Roles(bot))
