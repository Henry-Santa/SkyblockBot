"""

Make sure you have a config.json in the working folder

it should be laid out like

{
    "token" : "Your Discord Token",
    "clientid": "Your Discord App's Client ID",
    "guildId": "Your Discord Server's id",
    "apiKey": "Your hypixel api key"
}

"""


import discord
import json
import requests as r
import time
url = "https://api.hypixel.net/skyblock/auctions"
MojangUrl = "https://sessionserver.mojang.com/session/minecraft/profile/"
minimumProf = 1000000
maxRisk = 15000000
bannedKeywords = ["Cosmetic", "Furniture", "Skin", "Jerry", "EnchantedBook", "Rune", "Pet", "[Lvl", "[", "Lvl","pet","theFish", "the Fish","thefish"]
reforges = ["Loving","Gentle","Odd","Fast","Fair","Epic","Sharp","Heroic","Spicy","Legendary","Dirty","Fabled","Suspicious","Gilded","Warped","Withered","Bulky","Salty","Treacherous","Stiff","Lucky","Very","Highly","Extremely","Thicc","Absolutely","Even More", "Wise","Strong","Superior","Heavy","Light","Perfect","Refined","Deadly","Fine","Grand","Hasty","Neat","Rapid","Unreal","Awkward","Rich","Precise","Spiritual","Headstrong","Clean","Fierce","Mythic","Pure","Smart","Titanic","Necrotic","Ancient","Spiked","Cubic","Reinforced","Loving","Ridiculous","Empowered","Giant","Submerged","Jaded","Bizarre","Itchy","Ominous","Pleasant","Pretty","Shiny","Simple","Strange","Vivid","Godly","Demonic","Forceful","Hurtful","Keen","Strong","Unpleasant","Zealous","Silky","Bloody","Shaded","Sweet","Moil","Toil","Blessed","Bountiful","Magnetic","Fruitful","Refined","Stellar","Mithraic","Auspicious","Fleet","Heated","Ambered"]
commandStringBak = "`# NEW AUCTION FLIP FOUND!\n /ah {0}\n Expected Profit : **{1}**\n Risk : {2}\n Item Name : {3}`"
commandString = ">>> __/ah__ **{0}**\n __Expected Profit__ : `{1}`\n __Risk__ : `{2}`\n __Item Name__ : `{3}`"
global toggled 
toggled = False
aborting = False
client = discord.Client()
global currentAuctions
currentAuctions = {}
def ChangeUUIDToUsername(uuid : str):
    return json.loads(r.get(MojangUrl + uuid).content).get("name")

def GetAh():
    global currentAuctions
    resp = r.get(url).content
    dicted = json.loads(resp)
    for i in range(int(dicted.get("totalPages"))):
        res = r.get(url+"?page=" + str(i))
        aucs = json.loads(res.content).get("auctions")
        for i in aucs:
            if i.get("bin"):
                if (i.get("category") == "misc") or (i.get("item_name") == "Enchanted Book") or (i.get("category") == "blocks"):
                    pass
                else:
                    index = (i.get("item_name"))
                    index = index.replace(" ", "")
                    for re in reforges:
                        index = index.replace(re,"")
                    if index in currentAuctions:
                        bop = currentAuctions[index]
                        bop = bop.append(i)
                    else:
                        currentAuctions[index] = [i]

def SortAh() -> list[dict]:
    global currentAuctions
    auctionsToReturn = []
    for i in currentAuctions.keys():
        bestAh = None
        bestAhPrice = 28888800000
        SecondAhPrice = 696969100000
        for a in currentAuctions[i]:
            if not bestAh:
                pass
            if a.get("starting_bid") < bestAhPrice:
                bestAh = a
                SecondAhPrice = bestAhPrice
                bestAhPrice = a.get("starting_bid")
            elif a.get("starting_bid") < SecondAhPrice:
                SecondAhPrice = a.get("starting_bid")
        addingItem = {"AhObj" : bestAh, "Profit" : SecondAhPrice-bestAhPrice}
        auctionsToReturn.append(addingItem)
    return auctionsToReturn
def checkMinProf(Array):
    FinalArray = []
    for i in Array:
        if i.get("Profit") > 100000000:
            pass
        elif i.get("Profit") >= minimumProf:
            FinalArray.append(i)
    return FinalArray

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global toggled
    global minimumProf
    global maxRisk
    if message.author == client.user:
        return
    if message.content.startswith('!'):
        if message.content == "!hello":
            await message.channel.send("Hey qt {0.mention}!".format(message.author))
        elif message.content == '!help':
            await message.channel.send(">>> Hey baby {0.mention}! we have some awesome commands \n``` - !abort (HENRY ONLY) \n - !hello \n - !getAh \n - !testMessage \n - !runCode (HENRY ONLY) \n - !checkVar \n !setMin #(min) \n !setMax #(max)```".format(message.author))
        elif message.content == "!abort":
            toggled == False
            global aborting
            aborting = True
            await message.channel.send("shutting down {0.mention}! Will be dead in 10 seconds".format(message.author))
            time.sleep(10)
            exit()
        elif message.content.startswith("!getAh"):
            await message.channel.send("Getting AH")
            global currentAuctions
            GetAh()
            await message.channel.send("Ah has been gotted, now sorting!")
            sortedAh = SortAh()
            await message.channel.send(">>> **Finding profitable auctions, enjoy profits rolling in!**")
            checkedProf = checkMinProf(sortedAh)
            for i in checkedProf:
                if i.get("AhObj").get("starting_bid") < maxRisk:
                    if len(i.get("AhObj").get("item_name").replace("✪", "")) + 5 == len(i.get("AhObj").get("item_name")):
                        user = ChangeUUIDToUsername(i.get("AhObj").get("auctioneer"))
                        await message.channel.send(commandString.format(user,i.get("Profit"),i.get("AhObj").get("starting_bid"),i.get("AhObj").get("item_name")))
                    elif len(i.get("AhObj").get("item_name").replace("✪", "")) == len(i.get("AhObj").get("item_name")):
                        user = ChangeUUIDToUsername(i.get("AhObj").get("auctioneer"))
                        await message.channel.send(commandString.format(user,i.get("Profit"),i.get("AhObj").get("starting_bid"),i.get("AhObj").get("item_name")))
            await message.channel.send("Finished")
        elif message.content == '!testMessage':
            await message.channel.send(commandString.format("TestUser","101","1001","TestItem"))
        elif message.content.startswith("!runCode ") and message.author.name +"#"+ message.author.discriminator == "HardShellTurtle#0001":
            print("|"+message.content[9::]+"|")
            eval(message.content[9::])
        elif message.content == "!checkVar":
            await message.channel.send(">>> Min prof : " + str(minimumProf/1000000) +"m\nMax risk : " + str(maxRisk/1000000) + "m")
        elif message.content.startswith("!set"):
            if message.content.startswith("!setMin "):
                minimumProf = int(message.content[9::])
            elif message.content.startswith("!setMax "):
                maxRisk = int(message.content[9::])
def RunProg():
    global toggled
    global aborting
    while not aborting and toggled:
        print(toggled)
        time.sleep(1)

client.run(json.loads(open('config.json', 'r').read()).get("token"))

