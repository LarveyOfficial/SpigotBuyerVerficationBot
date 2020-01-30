<h1>Spigot Buyer Verification Bot</h1>

**WARNING**

I do not own nor have the rights to _https://www.spigotmc.org/resources/spigotbuyercheck.45155/_ I only use it as a tool and is Open Source. If you have issues setting it up please contact me at Larvey#0001 on discord.

**Prep**

1. Go to _https://discordapp.com/developers/applications/_ and setup a new application.

2. Go under Bot, and create a new Bot. Copy the token. **DO NOT SHARE IT**. You will set this token in your Config.py file.

**Instructions**

1. Clone Repo or download as Zip

2. Install requirements.txt

3. Modify sampleConfig.py except for BuyerPageURL to your info.

4. Visit _https://www.spigotmc.org/resources/spigotbuyercheck.45155/_

5. Once WireFly is running and setup, make sure either the bot is running on the same Network, Server, or VPS. If it is not, make sure the URL for the page is port forwarded and set BuyerPageURL equal to the IP Address of the website.

6. Make sure when setting the URL that it ends in /" Example: BuyerPageURL = "192.168.1.1:8080/SpigotBuyerCheck-1.0-SNAPSHOT/"

7. Start main.py with ``python3 main.py``

