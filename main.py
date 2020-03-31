import time
import random
import re
import requests
from PIL import Image
from io import BytesIO
import telepot
from telepot.loop import MessageLoop
from bs4 import BeautifulSoup as bs
bot = telepot.Bot('token')
leaderboard = {}
nameMon = ''
ingame = False
actMon = {}
usernames = {}
modMon = 0
names = open("pkmn.txt", "r+").readlines()
def handle(msg):
    # Vi prego non ammazzatemi per le variabili globali
    global ingame, leaderboard, actMon, nameMon, usernames, modMon

    command = msg['text'].split(' ')[0]
    userId = msg['from']['id']
    chatId = msg['chat']['id']
    if command=="/help" or command=="/start":
        bot.sendMessage(chatId, "Ciao! I comandi sono molto semplici:\n\n🕹️ Con /whois iniziano i giochi! Il bot manderà una foto zoomata di un Pokémon, il primo che manda il nome del Pokémon in questione vince!\n📃 Con /leaderboard viene mandata la classifica relativa al gruppo\n🏳️ Se un moderatore manda il commando /surrend, il gioco finirà senza alcun vincitore e verrà rivelato il Pokémon attuale\n✏️ Se un moderatore manda il comando /set, la modalità di selezione del Pokémon dagli utenti cambierà")
    if not ingame:
        if command=="/whois":
            # Metto in nameMon il nome di un Pokemon, scelto random dal file pkmn.txt, sostituendo spazi con trattini
            nameMon = "-".join(re.findall("[a-zA-Z]+", random.choice(names))).lower()

            # Apro con PIL un'immagine remota, prendendola per ora da PokemonDB, così posso avere praticamente ogni mon
            img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content))

            # Scelgo coordinate di un punto random, distante almeno 100px da ogni lato dell'immagine così da non avere immagini indecifrabili e non avere problemi col crop
            pointOfCrop = (random.randrange(100, stop=img.size[0]-100), random.randrange(100, stop=img.size[1]-100))

            # Croppo un quadrato di 100px*100px
            randomCrop = (pointOfCrop[0], pointOfCrop[1], 100+pointOfCrop[0], 100+pointOfCrop[1])

            print(nameMon)
            img = img.crop(randomCrop).save("pokemon.jpg")
            ingame = True

            # Setto come mon attuale per la chat il mon selezionato randomicamente prima, rimettendo gli spazi al loro posto, sia con le iniziali maiuscole che minuscole
            actMon[chatId] = (nameMon.title().replace('_',' '), nameMon.replace('_',' '))

            mId = bot.sendMessage(chatId, "🏁 Pronti? Si parte tra 5...")
            time.sleep(1)
            for i in range(4, 0, -1):
                bot.editMessageText(telepot.message_identifier(mId), "🏁 Pronti? Si parte tra %d..." % i)
                time.sleep(1)
            bot.deleteMessage(telepot.message_identifier(mId))
            bot.sendPhoto(chatId, open("pokemon.jpg", "rb"), "Chi è quel Pokémon?")

        if command == "/leaderboard":
            count = 0
            printStr = "📃 Classifica 📃\n\n"
            for user in leaderboard[chatId].keys():
                count += 1
                if count==1:
                    printStr += '🥇 '
                elif count==2:
                    printStr += '🥈 '
                elif count==3:
                    printStr += '🥉 '
                else:
                    printStr += str(count)+'. '

                printStr += "@"+usernames[user]+": "+str(leaderboard[chatId][user])

                if leaderboard[chatId][user]==1:
                    printStr += " punto\n" 
                else:
                    printStr += " punti\n"
            
            bot.sendMessage(chatId, printStr)

        if command == "/set":
            if bot.getChatMembersCount(chatId)<3: # Se la chat è formata da un solo utente
                if modMon==0:
                    modMon=1
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Qualunque nel messaggio\" a \"Nome esatto\" ✏️") 
                else:
                    modMon=0
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Nome esatto\" a \"Qualunque nel messaggio\" ✏️") 
            # Se la chat è un gruppo, controlla che l'utente del messaggio sia tra gli amministratori
            elif userId in [i['user']['id'] for i in bot.getChatAdministrators(chatId)]:
                if modMon==0:
                    modMon=1
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Qualunque nel messaggio\" a \"Nome esatto\" ✏️") 
                else:
                    modMon=0
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Nome esatto\" a \"Qualunque nel messaggio\" ✏️") 
            else:
                bot.sendMessage(chatId, "Ehy, " + msg['from']['first_name'] + ' non sei un moderatore!')
    if ingame:

        # Se la modalità settata con /set è 0, il Pokemon viene cercato in tutta la stringa, altrimenti la stringa deve essere esattamente uguale al nome del Pokemon
        if (((actMon[chatId][0] in msg['text']) or (actMon[chatId][1] in msg['text'])) and modMon==0) or msg['text']==actMon[chatId][0]:
            img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content)).save("pokemon.jpg")
            bot.sendPhoto(chatId, open("pokemon.jpg", "rb"),"🏅 Complimenti %s!\nIl Pokémon corretto era %s! \n🕹️ Usare il comando /whois per riprovare \n📃 Usare il comando /leaderboard per la classifica" \
                                                            % (msg["from"]["first_name"], actMon[chatId][0]))
            actMon[chatId] = ('', '')
            ingame = False

            # Dizionario con gli username per stampare la classifica in maniera più carina
            if userId not in usernames:
                usernames[userId] = msg['from']['username']
            # Se l'utente ha cambiato nickname, questo cambio verrà preso in considerazione
            elif usernames[userId]!=msg['from']['username']:
                usernames[userId] = msg['from']['username']
            # Se il gruppo non è presente tra i gruppi che hanno una classifica, viene aggiunto
            if chatId not in leaderboard:
                leaderboard[chatId] = {}
            # Se l'utente non ha mai vinto, esso viene aggiunto alla classifica con un punteggio di 1 dato che ha appen vinto un game
            if userId not in leaderboard[chatId]:
                leaderboard[chatId][userId] = 1
            else:
                leaderboard[chatId][userId] += 1
        if command=="/surrend":
            # Se la chat è formata da un solo utente
            if bot.getChatMembersCount(chatId)<3:
                img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content)).save("pokemon.jpg")
                bot.sendPhoto(chatId, open("pokemon.jpg", "rb"),"🏳️ Il Pokémon corretto era %s! \n🕹️ Usare il comando /whois per riprovare \n📃 Usare il comando /leaderboard per la classifica" \
                                                                % (actMon[chatId][0]))
                actMon[chatId] = ('', '')
                ingame = False

            # Se la chat è un gruppo, controlla che l'utente del messaggio sia tra gli amministratori
            elif userId in [i['user']['id'] for i in bot.getChatAdministrators(chatId)]:
                img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content)).save("pokemon.jpg")
                bot.sendPhoto(chatId, open("pokemon.jpg", "rb"),"🏳️ Il Pokémon corretto era %s! \n🕹️ Usare il comando /whois per riprovare \n📃 Usare il comando /leaderboard per la classifica" \
                                                                % (actMon[chatId][0]))
                actMon[chatId] = ('', '')
                ingame = False
            else:
                bot.sendMessage(chatId, "Ehy, " + msg['from']['first_name'] + ' non sei un moderatore!')
MessageLoop(bot, handle).run_as_thread()
while 1:
    time.sleep(10)
