import random
import string

import Config
import cloudscraper
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

scraper = cloudscraper.create_scraper()


class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # Main Verify Command Required Spigot ID
    async def verify(self, ctx, *, id: str = None):
        if id is None:
            print("User did not input ID")
            embed = discord.Embed(
                title="ERROR",
                description="Please provide a User ID",
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        else:
            # Checks if user is already verified or in verification process, if not checks if ID is already in use.
            print("Finding Doc")
            doc = Config.USERS.find_one({"user_id": ctx.author.id})
            print("Doc Found Testing if None or Not")
            print("Finding Spigot ID")
            spigotid = Config.USERS.find_one({"Spigot ID": id})
            print("Testing if Spigot ID is none or Not")
            if doc is None:
                print("Doc is none")
                if spigotid is None:
                    print("SpigotID is none")
                    spigot = scraper.get("https://www.spigotmc.org/members/" + id)  # Pulls up ID Page
                    print("Got Spigotmc.org")
                    page = BeautifulSoup(spigot.content, "html.parser")
                    print("Parsed HTML")
                    if not page.find_all('div', attrs={
                        "class": "mainText secondaryContent"}):  # Checks if Page is real Member or fake ID
                        print("User does not exist")
                        embed = discord.Embed(
                            title="ERROR",
                            description="That is not a valid ID",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                    else:
                        print("Scraping Buyer Page")
                        buyurl = scraper.get(Config.BuyerPageURL + id)  # Checks if user has purchased product
                        print("Grabbed Buyer Page")
                        buypage = BeautifulSoup(buyurl.content, "html.parser")
                        print("Parsed HTML")
                        if buypage.find_all('div', attrs={
                            "class": "alert alert-danger tool-msg"}):  # If False, user has not purchased a product.
                            print("User didnt buy :(")
                            embed = discord.Embed(
                                title="No Purchase Found",
                                description="You have not purchased any product from this store.",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                        else:  # User has purchased a product
                            print("User purchased :D")
                            user_name = buypage.find('h3').text
                            stringLength = 25
                            letters = string.ascii_lowercase
                            secretCode = ''.join(random.choice(letters) for i in range(stringLength))
                            print("Secret Code Picked: " + secretCode)
                            Config.USERS.insert_one(
                                {"user_id": ctx.author.id, "secretCode": secretCode, "verified": False,
                                 "user_name": user_name, "Spigot ID": id})  # Inserts User into the MongoDB
                            embed = discord.Embed(
                                title="Verify Identity",
                                description="Please change your status on Spigot to: \n > ||`" + secretCode + "`|| < \nThen use `v!statusCheck` to continue verification",
                                color=Config.MAINCOLOR
                            )
                            await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="ERROR",
                        description="That ID is already in Use",
                        color=Config.ERRORCOLOR
                    )
                    await ctx.send(embed=embed)
            elif not doc['verified']:
                embed = discord.Embed(
                    title="Verify Identity",
                    description="Please change your status on Spigot to your secret code provided, then use `v!statusCheck` to finish verification",
                    color=Config.MAINCOLOR
                )
                await ctx.send(embed=embed)
            elif doc['verified']:
                embed = discord.Embed(
                    title="Verify Identity",
                    description="You have already been verified",
                    color=Config.MAINCOLOR
                )
                await ctx.send(embed=embed)

    @commands.command()
    # Checks user status on Spigot
    async def statusCheck(self, ctx):
        doc = Config.USERS.find_one({"user_id": ctx.author.id})
        if doc is None:  # Checks if user has done v!verify command
            embed = discord.Embed(
                title="ERROR",
                description="Please use `v!verify <ID>` to start verification",
                color=Config.ERRORCOLOR
            )
            await ctx.send(embed=embed)
        elif doc['verified']:  # Checks if user is already Verified
            embed = discord.Embed(
                title="Verify Identity",
                description="You are already verified",
                color=Config.MAINCOLOR
            )
            await ctx.send(embed=embed)
        else:
            id = doc['Spigot ID']
            spigot = scraper.get("https://www.spigotmc.org/members/" + id)
            page = BeautifulSoup(spigot.content, "html.parser")
            for match in page.find_all(
                    'span'):  # Removes all <span></span> from HTML code as it interfeered with status
                match.replace_with('')
            table = page.find_all('div', attrs={"class": "mainText secondaryContent"})
            if not table:  # Will never happen unless DB manually changed
                embed = discord.Embed(
                    title="CRITICAL ERROR",
                    description="An Unknown Error has occured, Please contact a Dev immediately",
                    color=Config.ERRORCOLOR
                )
                await ctx.send(embed=embed)
            else:
                for x in table:
                    userStatus = x.find('p', attrs={"class": "userStatus"})
                    if userStatus is None:
                        embed = discord.Embed(
                            title="ERROR",
                            description="Please go in Spigot and change your status to the Secret Code and try again \n If this error continues please contact a Dev.",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)
                    elif doc['secretCode'] in userStatus.text:
                        role = discord.utils.get(ctx.guild.roles, id=int(Config.VerifiedRoleID))
                        Config.USERS.update_one({"user_id": ctx.author.id}, {"$set": {"verified": True}})
                        await ctx.author.add_roles(role)  # Gives user Verified Role
                        embed = discord.Embed(
                            title="Success!",
                            description="Your Discord Account has been verified and given the Verified Role!",
                            color=Config.MAINCOLOR
                        )
                        await ctx.send(embed=embed)
                        doc = Config.USERS.find_one({"user_id": ctx.author.id})
                        buyurl = scraper.get(
                            Config.BuyerPageURL + str(doc['Spigot ID']))  # Checks if user has purchased product
                        buypage = BeautifulSoup(buyurl.content, "html.parser")
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
                        index = 0
                        teardown = data["bought"]  # removes first part of json
                        if teardown:  # IDK why but it checks if user purchased stuff.... Ya never know.
                            for item in teardown:
                                itemdoc = Config.PLUGINS.find_one({'id': int(teardown[index]["id"])})
                                if itemdoc is not None:
                                    role = discord.utils.get(ctx.guild.roles, id=int(itemdoc['roleid']))
                                    if role is not None:
                                        await ctx.author.add_roles(role)
                                index += 1
                    else:
                        embed = discord.Embed(
                            title="ERROR",
                            description="Please go in Spigot and change your status to the Secret Code and try again \n If this error continues please contact a Dev.",
                            color=Config.ERRORCOLOR
                        )
                        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Help",
            description="**Verification**\n`v!verify <ID>` - Verify as a Buyer\n**Roles**\n`v!role join <RoleName>` - Join a Role(If purchased)\n`v!role leave <RoleName>` - Leave a role\n\nYour ID can be found in your Spigot Profile URL.",
            color=Config.MAINCOLOR
        )
        file = discord.File("help.jpg", filename="help.jpg")
        embed.set_image(url="attachment://" + "help.jpg")
        await ctx.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(Verification(bot))
