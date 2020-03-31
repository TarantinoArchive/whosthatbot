import time
import random
import re
import requests
from PIL import Image
from io import BytesIO
import telepot
from telepot.loop import MessageLoop
from bs4 import BeautifulSoup as bs
bot = telepot.Bot('1089841308:AAGAo5g_Wir3-a61zYjxEbXa6c3aiKt0JAU')
leaderboard = {}
nameMon = ''
inGame = {}
actMon = {}
usernames = {}
defaultLen = {}
activeHelps = {}
maxMess = {}
modMon = {}
names = open("pkmn.txt", "r+").readlines()
messageCount = {}
alreadySelectedLetters = {}
def handle(msg):
    # Vi prego non ammazzatemi per le variabili globali
    global inGame, leaderboard, actMon, nameMon, usernames, modMon

    msgText = msg['text'].split(' ')
    if len(msgText)>1: command, params = msgText[0], msgText[1:]
    else: command, params = msgText[0], ''

    userId = msg['from']['id']
    chatId = msg['chat']['id']
    if chatId not in inGame:
        inGame[chatId] = False
        maxMess[chatId] = 20
        activeHelps[chatId] = True
        defaultLen[chatId] = 1
        modMon[chatId] = 0

    if command=="/help" or command=="/start":
        bot.sendMessage(chatId, "Ciao! I comandi sono molto semplici:\n\n🕹️ Con /whois iniziano i giochi! Il bot manderà una foto zoomata di un Pokémon, il primo che manda il nome del Pokémon in questione vince!\n📃 Con /leaderboard viene mandata la classifica relativa al gruppo\n🏳️ Se un moderatore manda il commando /surrend, il gioco finirà senza alcun vincitore e verrà rivelato il Pokémon attuale\n✏️ Se un moderatore manda il comando /set, la modalità di selezione del Pokémon dagli utenti cambierà")
    
    if not inGame[chatId]:
        if command=="/setHelp":
            if bot.getChatMembersCount(chatId)<3 or userId in [i['user']['id'] for i in bot.getChatAdministrators(chatId)]:
                if len(params)>0:
                    if params[0] in 'trueTrue':
                        activeHelps[chatId] = True
                        bot.sendMessage(chatId, "ℹ️ Aiuti attivati ℹ️")
                    elif params[0] in 'falseFalse':
                        activeHelps[chatId] = False
                        bot.sendMessage(chatId, "ℹ️ Aiuti disattivati ℹ️")
                    elif params[0] == "lunghezza":
                        if params[1].isdigit():
                            defaultLen[chatId] = int(params[1])
                            bot.sendMessage(chatId, "ℹ️ Lunghezza massima dell'aiuto impostata a %s ℹ️" % params[1])
                        else:
                            bot.sendMessage(chatId, "⚠️ Parametro non corretto ⚠️")
                    elif params[0] == "messaggi":
                        if params[1].isdigit():
                            maxMess[chatId] = int(params[1])
                            bot.sendMessage(chatId, "ℹ️ Numero di messaggi prima dell'aiuto impostato a %s ℹ️" % params[1])
                        else:
                            bot.sendMessage(chatId, "⚠️ Parametro non corretto ⚠️")
                else:
                    bot.sendMessage(chatId, "⚠️ Parametro non corretto ⚠️")
            else:
                bot.sendMessage(chatId, "Ehy, " + msg['from']['first_name'] + ' non sei un moderatore!')
        
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
            inGame[chatId] = True

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
            # Se la chat è formata da un solo utente o l'utente è un moderatore
            if bot.getChatMembersCount(chatId)<3 or userId in [i['user']['id'] for i in bot.getChatAdministrators(chatId)]: 
                if modMon[chatId]==0:
                    modMon[chatId]=1
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Qualunque nel messaggio\" a \"Nome esatto\" ✏️") 
                else:
                    modMon[chatId]=0
                    bot.sendMessage(chatId, "✏️ Modalità cambiata da \"Nome esatto\" a \"Qualunque nel messaggio\" ✏️") 
            else:
                bot.sendMessage(chatId, "Ehy, " + msg['from']['first_name'] + ' non sei un moderatore!')
    if inGame[chatId]:

        # Ogni 20 messaggi, se gli amministratori avranno scelto di sì, il bot manderà un aiuto ai partecipanti, indicando una lettera random del nome del Pokémon
        if chatId not in messageCount:
            messageCount[chatId] = 0
            alreadySelectedLetters[chatId] = []
        messageCount[chatId] += 1
        
        # Se il contatore di messaggi è arrivato ad un multiplo di 20 e il numero di lettere date è minore del numero impostato, manda un aiuto
        if messageCount[chatId]%maxMess[chatId]==0 and len(alreadySelectedLetters[chatId])<len(actMon[chatId][1])-defaultLen[chatId] and activeHelps[chatId]:
            # Sceglie una lettera random della stringa finchè non gli esce una lettera ancora sconosciuta ai giocatori
            while 1:
                randomLetter = random.randrange(0, stop=len(actMon[chatId][1]))
                if randomLetter not in alreadySelectedLetters[chatId]:
                    break
            
            alreadySelectedLetters[chatId].append(randomLetter)

            # Seleziono le lettere conosciute e sostituisco le altre con degli underscore
            printMon = ''.join([actMon[chatId][1][l] for l in sorted(alreadySelectedLetters[chatId])])
            for i in range(len(actMon[chatId][1])):
                if i>=len(printMon):
                    break
                if printMon[i]!=actMon[chatId][1][i]:
                    listLetters = [c for c in printMon]
                    listLetters.insert(i, '_')
                    printMon = ''.join(listLetters)
            bot.sendMessage(chatId, "❗ La %s lettera è la %s ❗\nIl nome fin'ora rivelato è :\n❗ %s ❗" % (str(randomLetter+1), actMon[chatId][1][randomLetter], printMon))
        
        # Se la modalità settata con /set è 0, il Pokemon viene cercato in tutta la stringa, altrimenti la stringa deve essere esattamente uguale al nome del Pokemon
        if (((actMon[chatId][0] in msg['text']) or (actMon[chatId][1] in msg['text'])) and modMon[chatId]==0) or msg['text']==actMon[chatId][0]:
            img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content)).save("pokemon.jpg")
            bot.sendPhoto(chatId, open("pokemon.jpg", "rb"),"🏅 Complimenti %s!\nIl Pokémon corretto era %s! \n🕹️ Usare il comando /whois per riprovare \n📃 Usare il comando /leaderboard per la classifica" \
                                                            % (msg["from"]["first_name"], actMon[chatId][0]))
            actMon[chatId] = ('', '')
            inGame[chatId] = False

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
            # Ordino la classifica
            leaderboard[chatId] = {k: i for (k, i) in sorted(leaderboard[chatId].items(), key=lambda kv:(kv[1], kv[0]), reverse=True)}
        if command=="/surrend":
            # Se la chat è formata da un solo utente o l'utente è un moderatore
            if bot.getChatMembersCount(chatId)<3 or userId in [i['user']['id'] for i in bot.getChatAdministrators(chatId)]:
                img = Image.open(BytesIO(requests.get("https://img.pokemondb.net/artwork/large/%s.jpg" % nameMon).content)).save("pokemon.jpg")
                bot.sendPhoto(chatId, open("pokemon.jpg", "rb"),"🏳️ Il Pokémon corretto era %s! \n🕹️ Usare il comando /whois per riprovare \n📃 Usare il comando /leaderboard per la classifica" \
                                                                % (actMon[chatId][0]))
                actMon[chatId] = ('', '')
                inGame[chatId] = False
            else:
                bot.sendMessage(chatId, "Ehy, " + msg['from']['first_name'] + ' non sei un moderatore!')
MessageLoop(bot, handle).run_as_thread()
while 1:
    time.sleep(10)
