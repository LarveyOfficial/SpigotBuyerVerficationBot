<h1>Spigot Buyer Verification Bot</h1>

**WARNING**

I do not own nor have the rights to _https://www.spigotmc.org/resources/spigotbuyercheck.45155/_ I only use it as a tool and is Open Source. If you have issues setting it up please contact me at Larvey#0001 on discord.

**Prep**

1. Go to _https://discordapp.com/developers/applications/_ and setup a new application.

2. Go under Bot, and create a new Bot. Copy the token. **DO NOT SHARE IT**. You will set this token in your Config.py file.

3. Go to _https://cloud.mongodb.com/_ and setup a new Account

4. Follow the instructions and start a new Cluster.

5. Select the free tier.

6. Once cluster is initialized continue to Network Access and add 0.0.0.0 to the IP list

7. Then Navigate to Database Access and make a Admin Account

8. Go to The cluster and click COLLECTIONS

9. When creating a Database make sure the database is named ``SpigotBuyerChecker``

10. Next go back to the Cluster page and click connect, once there select Connect Your Application

11. Change the Driver to python, and select Version 3.6 or later.

12. Copy the Connection String Only and modify the <password> argument to contain the password from step 7.

**Instructions**

1. Clone Repo or download as Zip

2. Install requirements.txt

3. Modify sampleConfig.py except for BuyerPageURL to your info. For DevIDs format like this: [123344532432, 23213324, 32424324324]

4. Visit _https://www.spigotmc.org/resources/spigotbuyercheck.45155/_

5. Once WireFly is running and setup, make sure either the bot is running on the same Network, Server, or VPS. If it is not, make sure the URL for the page is port forwarded and set BuyerPageURL equal to the IP Address of the website.

6. Make sure when setting the URL that it ends in /" Example: BuyerPageURL = "192.168.1.1:8080/SpigotBuyerCheck-1.0-SNAPSHOT/"

7. Next add the DB Connection String from step 12 in Prep into the "" For CLUSTER. _It should look like: ``CLUSTER = pymongo.MongoClient("CONNECTION_STRING")``_

8. Start main.py with ``python3 main.py``

**Commands**

>_**User Commands**_

``v!help`` - Displays help Command

``v!verify <SpigotID>`` - Starts Verification Process

``v!StatusCheck`` - After **v!verify** This will check if you changed your status to the secretCode.

``v!role list`` - List Current _Premium_ Plugins users can join.

``v!role join <pluginName>`` - Adds user to Plugin Role if they are verified and have purchased the plugin.

``v!role leave <pluginName>`` - Removes user from Plugin Role if they are in it.

>_**Admin Commands**_.

_Admins must have their Discord ID's in Config > DevIds_

``v!role add`` - Starts process of adding a role to the DB/List

``v!role remove`` - Removes a Role from the DB/List

``v!restart`` - Restarts Roles and Verification Commands.