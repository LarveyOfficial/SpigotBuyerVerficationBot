import pymongo

# Change File Name to Config.py Once info is set.

TOKEN = ""

CLUSTER = pymongo.MongoClient("")

USERS = CLUSTER['SpigotBuyerChecker']['users']

PLUGINS = CLUSTER['SpigotBuyerChecker']['plugins']

BuyerPageURL = ""

DEVIDS = []

MAINCOLOR = 0x8A2BE2
ERRORCOLOR = 0xED4337

VerifiedRoleID = 000000
