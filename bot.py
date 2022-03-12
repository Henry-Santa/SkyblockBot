"""

Make sure you have a config.json in the working folder

it should be laid out like

{
    "token" : "Your Discord Bot's Token",
}

"""
#Import some dependencies
import time
try:
    import discord
except:
    print("make sure to do pip3 install discord\n")
    time.sleep(10)
    exit()
import json
import requests as r

url = "https://api.hypixel.net/skyblock/auctions" #skyblock ah url (will be used later)
MojangUrl = "https://sessionserver.mojang.com/session/minecraft/profile/" #Turn UUID to playername url (will be used later)


#Change these variables if you would like to
minimumProf = 500000
maxRisk = 10000000


bannedKeywords = ["Cosmetic", "Furniture", "Skin", "Jerry", "EnchantedBook", "Rune", "Pet", "[Lvl", "[", "Lvl","pet","theFish", "the Fish","thefish"] # Stuff that can be easily market manipulated or for the EnchantedBook, stuff I don't care to deal with
#                                                                          |
#All reforges, this is used to get the item name without the reforge later v
reforges = ["Fair","Renowned","Loving","Gentle","Odd","Fast","Fair","Epic","Sharp","Heroic","Spicy","Legendary","Dirty","Fabled","Suspicious","Gilded","Warped","Withered","Bulky","Salty","Treacherous","Stiff","Lucky","Very","Highly","Extremely","Thicc","Absolutely","Even More", "Wise","Strong","Superior","Heavy","Light","Perfect","Refined","Deadly","Fine","Grand","Hasty","Neat","Rapid","Unreal","Awkward","Rich","Precise","Spiritual","Headstrong","Clean","Fierce","Mythic","Pure","Smart","Titanic","Necrotic","Ancient","Spiked","Cubic","Reinforced","Loving","Ridiculous","Empowered","Giant","Submerged","Jaded","Bizarre","Itchy","Ominous","Pleasant","Pretty","Shiny","Simple","Strange","Vivid","Godly","Demonic","Forceful","Hurtful","Keen","Strong","Unpleasant","Zealous","Silky","Bloody","Shaded","Sweet","Moil","Toil","Blessed","Bountiful","Magnetic","Fruitful","Refined","Stellar","Mithraic","Auspicious","Fleet","Heated","Ambered"]
# Backup command string (not used)
commandStringBak = "`# NEW AUCTION FLIP FOUND!\n /ah {0}\n Expected Profit : **{1}**\n Risk : {2}\n Item Name : {3}`"
# Change this to however you would like your discord messages to be formatted, but the default works well
commandString = ">>> __/ah__ **{0}**\n __Expected Profit__ : `{1}`\n __Risk__ : `{2}`\n __Item Name__ : `{3}`"

#Create discord client
client = discord.Client()

#Defining the global variable for the current auctions
global currentAuctions
currentAuctions = {}

#Basic function to change uuid to a username (just so the code is prettier later on)
def ChangeUUIDToUsername(uuid : str):
    return json.loads(r.get(MojangUrl + uuid).content).get("name")

#Gets all ah auctions and adds them to the global current auctions
def GetAh():
    global currentAuctions
    currentAuctions = {} #Reset the current auctions from past use (memory saving line)
    
    #Finds the amount of PAGES of auctions!
    resp = r.get(url).content
    dicted = json.loads(resp)

    #Goes through every page of auctions and adds them to the auction list if they are BIN
    for i in range(int(dicted.get("totalPages"))):
        
        # Gets a page depicted by i
        res = r.get(url+"?page=" + str(i))
        aucs = json.loads(res.content).get("auctions")
        
        # Goes through this pages auctions (I know this solution is slow)
        for i in aucs:
            if i.get("bin"):
                # checks the item gets through the checks to make sure it is probably flippable and also I need some HELP to check if the item contains the banned keywords
                if (i.get("category") == "misc") or (i.get("item_name") == "Enchanted Book") or (i.get("category") == "blocks") or (i.get("item_name") == "Egg the Fish"):
                    pass
                else:
                    # Add this item to the list of auctions for the same item ignoring enchants sorry
                    index = (i.get("item_name"))
                    index = index.replace(" ", "")
                    index = index.replace("⚚","")
                    # Remove the reforge for indexing it
                    for re in reforges:
                        index = index.replace(re,"")
                    if index in currentAuctions:
                        # If this index already exists, add this to a list of them
                        if len(index.get("AhObj").get("item_name").replace("✪", "")) + 5 == len(i.get("AhObj").get("item_name")):
                            bop = currentAuctions[index]
                            bop = bop.append(i)
                        else:
                            bop = currentAuctions[index.replace("✪", "")]
                            bop = bop.append(i)
                    else:
                        # Create the first refrence of this item and give it an index in the dictionary!
                        currentAuctions[index] = [i]

# Sorts the ah to find the best and second best auction of any item, with the expected profit of that item! (This is where magic happens!)
def SortAh() -> list[dict]:
    global currentAuctions # Get the global auctions
    auctionsToReturn = [] # Best auctions and how many coins it will profit you!

    # For each item find the best auction
    for i in currentAuctions.keys():
        bestAh = None # create vars
        bestAhPrice = 28888800000 
        SecondAhPrice = 696969100000 # this number is ridiculously large make sure that when we see an impossibly high profit, it isn't real! 
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
    # I don't want to explain how all of that works! so figure it out ^
    #                                                                 |
    #                                                                 |
    return auctionsToReturn # Return all them good profits



# Check that it meets the minimum profit req
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
    # Just som basic log on stuff
    print('We have logged in as {0.user}'.format(client))
    time.sleep(10)
    status = discord.Game("Min Prof = {0}m ---- Max Risk = {1}m".format(minimumProf/1000000, maxRisk/1000000))
    await client.change_presence(status=discord.Status.idle, activity=status)
# When the bot recieves a message anywhere
@client.event
async def on_message(message):
    # getting the global variables this script needs to work!
    global minimumProf
    global maxRisk
    # If the bot send a message don't do anything to it
    if message.author == client.user:
        return
    # Check that the message starts with the prefix
    if message.content.startswith('!'):
        # Basic commands for fun cuz why not haha
        if message.content == "!hello":
            await message.channel.send("Hey qt {0.mention}!".format(message.author))
        elif message.content == '!help':
            await message.channel.send(">>> Hey baby {0.mention}! we have some awesome commands \n``` - !abort (OWNER ONLY) \n - !hello \n - !getAh \n - !testMessage \n - !runCode (OWNER ONLY) \n - !checkVar \n !setMin #(min) \n !setMax #(max)```".format(message.author))
        elif message.content == "!abort":
            await message.channel.send("shutting down {0.mention}! Will be dead in 10 seconds".format(message.author))
            time.sleep(10)
            exit()
        
        # run through the functions we declared earlier
        elif message.content.startswith("!getAh"):
            await message.channel.send("Getting AH") # Status update
            global currentAuctions
            GetAh() # Get all the auctions
            await message.channel.send("Ah has been gotted, now sorting!") # Status update
            sortedAh = SortAh() # Sort the auctions
            await message.channel.send(">>> **Finding profitable auctions, enjoy profits rolling in!**") # Status update
            checkedProf = checkMinProf(sortedAh) # Go through those sorted auctions and make sure they meet the minimum reqs
            for i in checkedProf:
                if i.get("AhObj").get("starting_bid") < maxRisk: # ensure nothing is out of our price range!
                    # Make sure the item is 5 star, as to price it like it
                    if len(i.get("AhObj").get("item_name").replace("✪", "")) + 5 == len(i.get("AhObj").get("item_name")):
                        user = ChangeUUIDToUsername(i.get("AhObj").get("auctioneer"))
                        await message.channel.send(commandString.format(user,i.get("Profit"),i.get("AhObj").get("starting_bid"),i.get("AhObj").get("item_name")))
                    # Everything else is just, considered no star
                    else:
                        user = ChangeUUIDToUsername(i.get("AhObj").get("auctioneer"))
                        await message.channel.send(commandString.format(user,i.get("Profit"),i.get("AhObj").get("starting_bid"),i.get("AhObj").get("item_name")))
            await message.channel.send("Finished") # Status update
        # Command to check that the command message is too your liking :)
        elif message.content == '!testMessage':
            await message.channel.send(commandString.format("TestUser","101","1001","TestItem"))
        # Check the min prof and max risk
        elif message.content == "!checkVar":
            await message.channel.send(">>> Min prof : " + str(minimumProf/1000000) +"m\nMax risk : " + str(maxRisk/1000000) + "m")
        # not currently working >:(
        elif message.content.startswith("!set"):
            if message.content.startswith("!setMin "):
                minimumProf = int(message.content[8::])
                await message.channel.send("set min prof to " + message.content[8::])
            elif message.content.startswith("!setMax "):
                maxRisk = int(message.content[8::])
                await message.channel.send("set max risk to " + message.content[8::])

# Start up the client
client.run(json.loads(open('config.json', 'r').read()).get("token"))

