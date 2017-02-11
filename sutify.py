import spotipy
import webbrowser
from spotipy import oauth2
from spotipy import util
import os
import time

class entry(object):
    def __init__(self, apiObject = None, debug = False):
        if(debug == False and apiObject != None):
            self.name = apiObject['name'].encode('ascii', 'ignore').decode('ascii')
            self.uri = apiObject['uri']
            self.id = apiObject['id']
        else:
            self.name = "Debug Entry"
            self.uri = 'DebugURI'
            self.id = 'DebugID'

class trackObject(entry):
    def __init__(self, apiObject = None, debug = False):
        super().__init__(apiObject, debug)
        if(debug == False and apiObject != None):
            self.duration = apiObject['duration_ms']
            self.tracknumber = apiObject['track_number']
            self.popularity = apiObject['popularity']
            self.artist = artistObject(apiObject['artists'][0])
            self.album = albumObject(apiObject['album'])
        else:
            self.duration = 0
            self.tracknumber = 0
            self.popularity = 50
            self.artist = artistObject(debug = True)
            self.album = albumObject(debug = True)

    def getPop(self):
        return self.popularity

    def stringFormat(self, nameChar = 25, artistChar = 12, albumChar = 20, durChar = 5, size = 'big'):

        if(size == 'small'):
            result = (sutil.wordSpacing(self.name, nameChar) + 
                " | " + self.artist.name)
        else:
            result = (sutil.wordSpacing(self.name, nameChar) + 
                " | " + sutil.wordSpacing(self.artist.name, artistChar) + 
                " | " + sutil.wordSpacing(self.album.name, albumChar) + 
                " | " + sutil.wordSpacing(sutil.durFormat(self.duration), durChar) + 
                " | " + "++++++++++"[:int(self.popularity/10)])

        return result

    def headerFormat(self, idChar = 4, nameChar = 25, artistChar = 12, smallTotalChar = 48, bigTotalChar = 90, size = 'big'):
        #output = []
        if size == 'small':
            return (sutil.align(sutil.wordSpacing('', 3 + idChar) + sutil.wordSpacing("Name", nameChar + 3) + "Artist", smallTotalChar) + '')

        else:
            return (sutil.align(sutil.wordSpacing('', 3 + idChar) + sutil.wordSpacing("Name", nameChar + 3) + sutil.wordSpacing("Artist", artistChar + 3) + "Album", bigTotalChar) + '')



class artistObject(entry):
    def __init__(self, apiObject = None, debug = False):
        super().__init__(apiObject, debug)

class albumObject(entry):
    def __init__(self, apiObject = None, debug = False):
        super().__init__(apiObject, debug)

class playlistObject(entry):
    def __init__(self, apiObject = None, debug = False, newclient = None):
        super().__init__(apiObject, debug)
        if(debug == False and apiObject != None and newclient != None):
            print("PlaylistObject constructor")
            self.ownerID = apiObject['owner']['id']
            self.playlistID = apiObject['id']
            self.owner = newclient.user(apiObject['owner']['id'])['display_name']
            if(self.owner == None):
                self.owner = ''
            else:
                self.owner = self.owner.encode('ascii', 'ignore').decode('ascii')
            self.trackCount = apiObject['tracks']['total']

    def stringFormat(self, nameChar = 43, ownerChar = 22, countChar = 5, size = 'big'):

        if(size == 'small'):
            result = (sutil.wordSpacing(self.name, nameChar - 25) + 
                " | " + self.owner)
        else:
            result = (sutil.wordSpacing(self.name, nameChar) + 
                " | " + sutil.wordSpacing(self.owner, ownerChar) + 
                " | " + str(self.trackCount))

        return result

    def headerFormat(self, idChar = 4, nameChar = 43, ownerChar = 22, smallTotalChar = 48, bigTotalChar = 90, size = 'big'):
        #output = []
        if size == 'small':
            return (sutil.align(sutil.wordSpacing('', 3 + idChar) + sutil.wordSpacing("Name", nameChar + 3 - 25) + "Owner", smallTotalChar) + '')

        else:
            return (sutil.align(sutil.wordSpacing('', 3 + idChar) + sutil.wordSpacing("Name", nameChar + 3) + sutil.wordSpacing("Owner", ownerChar + 3) + "Track Count", bigTotalChar) + '')



class block(object):
    def __init__(self, name = 'Unnamed Block', entries = [], type = 'default', status = 'big'):
        self.name = name
        self.entries = entries
        self.type = type
        print("block constructor: using status value " + status)
        self.status = status
        self.printlist = []
        self.position = 0
        self.orderingdata = {} #display index maps to entries index
        self.setupOrder()

    def diff(self, otherBlock, mode = 'match'):
        counter = 0
        print("Diff() comparing block " + str(self.position) + " with block " + str(otherBlock.position))
        print("Len(self.entries) = " + str(len(self.entries)))
        listOfMyID = []
        listOfOtherID = []
        for entry in self.entries:
            listOfMyID.append(entry.id)
        for entry in otherBlock.entries:
            listOfOtherID.append(entry.id)

        for myEntry in self.entries:
            print("Checking an entry out...")
            if(myEntry.id in listOfOtherID):
                print("Found the entry '" + myEntry.name + "' in the other block!")
                time.sleep(1)
                print("Setting orderingdata[" + str(counter) + "] to " + str(listOfOtherID.index(myEntry.id)))
                otherBlock.orderingdata[counter] = listOfOtherID.index(myEntry.id)
            else:
                otherBlock.orderingdata[counter] = -1
            counter +=1

    def setupOrder(self):
        for entryCounter in range(len(self.entries)):
        	self.orderingdata[entryCounter] = entryCounter

    def generatePrintlist(self, smallTotalChar = 48, bigTotalChar = 90):

        nameChar = 25 #maybe replace with prefs file?
        artistChar = 12
        albumChar = 20
        idChar = 4
        durChar = 6
        lineLength = bigTotalChar

        self.printlist = []
        if self.status == 'small':
            print("Generating printlist for small block")
            lineLength = smallTotalChar
            self.printlist.append(sutil.align("  Block " + str(self.position + 1) + ": " + self.name, smallTotalChar))
            self.printlist.append(sutil.align("  " + sutil.generateBorder('=', smallTotalChar), smallTotalChar) + '')
        elif self.status == 'big':
            print("Generating printlist for big block")
            lineLength = bigTotalChar
            self.printlist.append(sutil.align("  Block " + str(self.position + 1) + ": " + self.name + ", with " + str(len(self.entries)) + " entries", bigTotalChar))
            self.printlist.append(sutil.align("  " + sutil.generateBorder('=', bigTotalChar), bigTotalChar) + '')

        if(len(self.entries) > 0):
            self.printlist.append(self.entries[0].headerFormat(size = self.status))

        counter = 1
        for entryCounter in range(max(list(self.orderingdata.keys()) + [0])+1):
            try:
                if(self.orderingdata[entryCounter] < 0):
                    raise KeyError
                newentry = self.entries[self.orderingdata[entryCounter]]
                content = "   " + sutil.wordSpacing(str(counter), idChar) + newentry.stringFormat(size = self.status)
            except KeyError:
                content = ''
            
            self.printlist.append(sutil.wordSpacing(content, lineLength) + '')
            counter += 1


        
        

class Sutify(object):

    def __init__(self):
        self.blocks = [] #List of lists of blocks

    def doSearch(self, query, specify = 'track'):
        rawsearchresults = self.client.search(query, type = specify, limit = 20)
        calculatedType = 'info'
        parsedSearchResults = []

        if(rawsearchresults == None):
            print("No search results :(")
            return []

        print("Search keys: " + str(rawsearchresults.keys()))

        for entryType in rawsearchresults.keys():
            calculatedType = entryType
            if(entryType == 'playlists'):
                for apiplaylist in rawsearchresults['playlists']['items']:
                    print("Beginning to construct playlist")
                    #print("Original object's owner's name is " + apiplaylist['owner']['name'])
                    #ownerid = apiplaylist['owner']['id']
                    #playlistid = apiplaylist['id']
                    parsedSearchResults.append(playlistObject(apiplaylist, newclient = self.client))
            elif(entryType == 'tracks'):
                for apitrack in rawsearchresults['tracks']['items']:
                    parsedSearchResults.append(trackObject(apitrack))
                parsedSearchResults.sort(key = trackObject.getPop, reverse = True)
            elif(entryType == 'albums'):
                for apialbum in rawsearchresults['albums']['items']:
                    parsedSearchResults.append(albumObject(apialbum))
            elif(entryType == 'artists'):
                for apiartist in rawsearchresults['artists']['items']:
                    parsedSearchResults.append(artistObject(apiartist))

        return (parsedSearchResults, calculatedType)

    def interpret(self, data):
        keywordList = data.split(" ")
        print("Interpreting " + str(keywordList))
        
        for i in range(len(keywordList)):
            #print("Looking at " + keywordList[i])



            if keywordList[i] == 'add':
                print("Found 'add'!")
                blockToAdd = None
                addStartIndex = i

                if(keywordList[addStartIndex+1] == 'search'):
                    print("Detected Search!")
                    searchStartIndex = addStartIndex+1
                    try:
                        searchQuery = sutil.isolateQuery(keywordList[searchStartIndex+1:])
                    except:
                        print(" sutify$ error: missing query")
                        break
                    print("Final search query: " + searchQuery)

                    acceptableModifiers = ['artist', 'album', 'track', 'playlist']
                    blocktype = 'info'

                    options, lastIndex = sutil.isolateOptions(keywordList, start = searchStartIndex+2, limit = 1)
                    modifier = None

                    if(len(options) > 0):
                        for option in options:
                            if option in acceptableModifiers:
                                modifier = option

                                print("Modifier is " + modifier)
                    
                    if modifier != None:
                        resultList, blocktype = self.doSearch(searchQuery, specify = modifier)
                    else:
                        resultList, blocktype = self.doSearch(searchQuery)

                    

                    blockToAdd = block(name = ('Search results for '+ searchQuery + ''), entries = resultList, type = blocktype, status = 'small')
                    #time.sleep(10)

                elif(keywordList[addStartIndex+1] == 'playlist'):
                    playlistStartIndex = addStartIndex+1
                    playlistName = keywordList[playlistStartIndex]

                elif(keywordList[addStartIndex+1] == 'mylist'):
                    mylistStartIndex = addStartIndex+1
                    if(keywordList[mylistStartIndex+1][0] == '-'):
                        if(keywordList[mylistStartIndex+1][1:] == 'playlist'):
                            pass

                elif(keywordList[addStartIndex+1] == 'debug'):
                    print("Making Debug block ('tracks')")
                    debugEntries = []
                    for i in range(20):
                        debugEntries.append(trackObject(debug = True))

                    blockToAdd = block(name = "Debug Block", entries = debugEntries, type = 'tracks')


                extraOptions, lastIndex = sutil.isolateOptions(keywordList, limit = 4)
                if(blockToAdd != None):
                    print("Beginning block add section")
                    insertIndex = 100
                    for option in extraOptions:
                        if option in ('big', 'small'):
                            print("Switching block status to " + option)
                            blockToAdd.status = option
                        if self.isSuitableIndex(option):
                            insertIndex = int(option)-1

                    #time.sleep(2)

                    self.smartAdd(blockToAdd, ind = insertIndex)
                    
                else:
                    print("blockToAdd = None")


                print("Block registry: ")
                print(repr(self.blocks))
                print(repr(self.blocks[-1:]))
                #time.sleep(5)

            if keywordList[i] == 'remove':
                startIndex = i
                if(self.isSuitableIndex(keywordList[startIndex+1])):
                    removeIndex = int(keywordList[startIndex+1])-1
                else:
                    if(keywordList[startIndex+1] == 'all'):
                        self.blocks = []
                        break
                    else:
                        print("Index incompatible.")
                        time.sleep(1)
                        break
                
                self.smartRemove(removeIndex)

                self.reshuffle()

            if keywordList[i] == 'move':
                startIndex = i

                if(self.isSuitableIndex(keywordList[startIndex+1]) and self.isSuitableIndex(keywordList[startIndex+2])):
                    moveStartIndex = int(keywordList[startIndex+1])-1
                    moveEndIndex = int(keywordList[startIndex+2])-1
                else:
                    print("Index incompatible.")
                    time.sleep(1)
                    break


                
   
                blockToMove = self.smartRemove(moveStartIndex)
                self.smartAdd(blockToMove, moveEndIndex)

            if keywordList[i] == 'diff':
                startIndex = i

                if(self.isSuitableIndex(keywordList[startIndex+1]) and self.isSuitableIndex(keywordList[startIndex+2])):
                    aIndex = int(keywordList[startIndex+1])-1
                    bIndex = int(keywordList[startIndex+2])-1

                    if(abs(aIndex-bIndex) != 1):
                        print("Basic index check failed, please try different blocks.")
                        time.sleep(1)
                        break

                else:
                    print("Index incompatible.")
                    time.sleep(1)
                    break

                allTheBlocks = sutil.collapseStructure(self.blocks)
                baseBlock = allTheBlocks[aIndex]
                secondaryBlock = allTheBlocks[bIndex]
                baseBlock.diff(secondaryBlock)
                
                self.renderAll()

            if keywordList[i] == 'play':
                startIndex = i

                if(self.isSuitableIndex(keywordList[startIndex+1])):
                    blockNumber = int(keywordList[startIndex+1])-1
                    #try:
                    entry = self.retrieveEntry(blockNumber, int(keywordList[startIndex+2])-1)
                    #except:
                        #print("Sorry, can't retrieve that entry.")
                        #time.sleep(1)
                        #break
                    webbrowser.open(entry.uri)

            if keywordList[i] == 'clear':
                startIndex = i
                print("Clear is parsing " + keywordList[i+1])
                if(self.isSuitableIndex(keywordList[startIndex+1])):
                    print("Clearing ordering data")
                    time.sleep(1)
                    sutil.collapseStructure(self.blocks)[int(keywordList[startIndex+1]) -1].setupOrder()
                    self.renderAll()

        time.sleep(0.5)
                #print("Todo: locate coordinate of block based on given number")




    def retrieveEntry(self, ind1, ind2):
        allTheBlocks = sutil.collapseStructure(self.blocks)
        return allTheBlocks[ind1].entries[ind2]

    def smartAdd(self, blockToAdd, ind = 100):
        print("SmartAdd!")
        allTheBlocks = sutil.collapseStructure(self.blocks)
        self.blocks = []
        allTheBlocks.insert(ind, blockToAdd)

        for bl in allTheBlocks:
            self.addBlock(bl)
 
        self.renderAll()

    def smartRemove(self, ind):
        print("SmartRemove!")
        allTheBlocks = sutil.collapseStructure(self.blocks)
        self.blocks = []
        output = allTheBlocks.pop(ind)

        for bl in allTheBlocks:
            self.addBlock(bl)

        self.renderAll()
        return output

    def reshuffle(self):
        allTheBlocks = sutil.collapseStructure(self.blocks)
        self.blocks = []
        for bl in allTheBlocks:
            self.addBlock(bl)


        self.renderAll()

    def isSuitableIndex(self, ind):
        try:
            int(ind)
        except ValueError:
            return False


        try:
            maxPosition = self.blocks[-1:][0][-1:][0].position
            return int(ind)-1 <= maxPosition
        except IndexError: #in this case, the blocks registry is likely empty.
            return True

        return False

    def processInterpretedBlock(self):
        pass

    def updateBlocksWithNewCounters(self):
        pass

    def renderAll(self):
        for row in self.blocks:
            for bl in row:
                if bl != None:
                    bl.generatePrintlist()

    def updatePositionCounters(self):
        blockcounter = 0

        for row in self.blocks:
            if(len(row) == 0):
                self.blocks.remove(row)
            else:
                for bl in row:
                    if bl != None:
                        bl.position = blockcounter
                        blockcounter += 1

    def addBlock(self, blockToAdd, ind = 100):
        counter = 0

        


        if len(self.blocks) == 0:
            #blockToAdd.position = 0
            print("addBlock: Nothing in blocks registry. Adding new row with the block with name " + blockToAdd.name)
            self.blocks.append([blockToAdd]) #if there is nothing in the blocks registry, add a new row, and add block
            #print(self.blocks)
            
        else:
            if len(self.blocks[-1:][0]) == 0: #if the last row is empty
                print("addBlock: Something in blocks registry. Nothing in last row, adding new block to last row.")
                self.blocks[-1:][0].append(blockToAdd) #append block to last row, regardless of block's size
                
            elif len(self.blocks[-1:][0]) == 1: #if there is one block in the last row

                if self.blocks[-1:][0][0].status == 'small' and blockToAdd.status == 'small': #if first block in row is small, and blockToAdd is small
                    
                    self.blocks[-1:][0].append(blockToAdd) #add to existing row

                else: #either first block in row is big, or blockToAdd is big, or both
                    self.blocks.append([blockToAdd]) #row is full with one big block, make a new one with the new block
            else:
                self.blocks.append([blockToAdd]) #row is full with two small blocks, make a new one with the new block

        self.updatePositionCounters()
        #blockToAdd.generatePrintlist()

    def displayAllBlocks2(self, smallTotalChar = 48, bigTotalChar = 90, nodelay = False):
        finalPrint = []
        masterCounter = 0
        #print(self.blocks)
        
        for row in self.blocks:
            rowPrint = []

            listOfLengths = []
            for block in row:
                #print("Printlist length: " + str(len(block.printlist)))
                #print("Ordering data length: " + str(len(block.orderingdata)))
                listOfLengths.append(len(block.printlist))
                #print("Appending blocklength " + str(len(block.printlist)) + "to list.")
            maxLines = 0
            if(len(listOfLengths) > 0):
                maxLines = max(listOfLengths)

            #print("maxLines = " + str(maxLines))
            #time.sleep(1)
            
            for i in range(maxLines):
                rowPrint.append('')

            for lineCounter in range(maxLines):
                
                for block in row:
                    try:
                        rowPrint[lineCounter] += block.printlist[lineCounter]
                    except IndexError:
                        if(block.status == 'small'):
                            rowPrint[lineCounter] += sutil.generateBorder(' ', smallTotalChar)
                        else:
                            rowPrint[lineCounter] += sutil.generateBorder(' ', bigTotalChar)
                        
                    rowPrint[lineCounter] += "    "

            #print(rowPrint)
            finalPrint.append('')
            finalPrint += rowPrint
            #finalPrint.append("   " + sutil.generateBorder("-", 90))
            finalPrint.append('')

        sutil.delayPrint(finalPrint, delay = not nodelay)


    



    def run(self):

        offlineDebug = False;

        os.system('cls' if os.name=='nt' else 'clear')
        logoFile = open('logo.txt')
        num_lines = sum(1 for line in logoFile)
        logoFile.seek(0)
        logoList = []
        for i in range(num_lines):
            lineToAdd = logoFile.readline().rstrip()
            logoList.append(lineToAdd)
        sutil.delayPrint(logoList)

        if(offlineDebug == False):
            self.token = sutil.login()
            self.client = spotipy.Spotify(self.token)
        else:
            print("Running in offline debug mode. Do not attempt to use any internet-enabled addblock commands.")

        time.sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')

        while True:
            self.displayAllBlocks2()
            print("\n")
            prompt = input(" sutify$ ")

            self.interpret(prompt)
            

            os.system('cls' if os.name=='nt' else 'clear')





class sutil(object):

    def generateBorder(char, length):
        return char * length;

    def collapseStructure(structure):
        output = []
        if(type(structure) != list):
            return [structure]
        for inner in structure:
            output += sutil.collapseStructure(inner)

        return output

    def durFormat(durms):
        totalseconds = durms/1000
        minutes = int(totalseconds/60)
        seconds = int(totalseconds) - (minutes*60)

        final = str(minutes)+':'+str(seconds).zfill(2)
        return final

    def align(content, spaces):
        sample = "                                                                       "
        if(len(content) <= spaces):
            return content + sample[:spaces-len(content)]
        if(len(content) > spaces):
            return content[:spaces]

    def wordSpacing(word, spaces):
        sample = "                                                                       "
        if(len(word) <= spaces):
            return word + sample[:spaces-len(word)]
        if(len(word) > spaces):
            return word[:spaces-2] + ".."

    def isolateQuery(data):
        startIndex = None
        endIndex = None
        for i in range(len(data)):
            print("Analyzing keyword: " + data[i])
            if data[i][0] == "'" or data[i][0] == '"':
                print("Found beginning quote!")
                startIndex = i
                break
        for i in range(startIndex, len(data)):
            print("Analyzing keyword: " + data[i])
            if data[i][-1] == "'" or data[i][-1] == '"':
                print("Found ending quote!")
                endIndex = i
                break

        isolatedList = data[startIndex:endIndex+1]
        isolatedList[0] = isolatedList[0].replace('"', '')
        isolatedList[-1] = isolatedList[-1].replace('"', '')

        query = " ".join(isolatedList)
        return query

    def isolateOptions(data, start = 0, limit = 1):
        counter = limit
        index = start - 1
        options = []

        for keyword in data[start:]:
            if keyword[0] == '-':
                if(counter > 0):
                    index += 1
                    options.append(keyword[1:])
                    counter -= 1

        return options, index


    def delayPrint(printlist, delay = True):
        
        for i in range(len(printlist)):
            try:
                print(printlist[i])
            except UnicodeEncodeError:
                print("Encoding error")
            time.sleep(0.02 * delay)

    def authenticate(username, scope = "playlist-modify-public playlist-modify-private playlist-read-collaborative"):
        redirect = "http://localhost:8888/callback/" #networking black magic
        credentialsFile = open('credentials.txt', 'r') #file containing Spotify app creds
        appID = credentialsFile.readline()
        appSecret = credentialsFile.readline()
        credentialsFile.close()

        appID = appID.rstrip()
        appSecret = appSecret.rstrip()

        spotifyAuthObject = spotipy.oauth2.SpotifyOAuth(appID, appSecret, redirect, scope = scope, cache_path = ".cache-" + username) #creates OAuth object that will control the OAuth loop

        authorization = spotifyAuthObject.get_cached_token() #tries to get cached auth token

        if not authorization:
            authPageURL = spotifyAuthObject.get_authorize_url() #get account authorization URL from auth data
            print(authPageURL)
            webbrowser.open(authPageURL)
            print("Opening authorization page. Please enter username and password.")
            authResult = input("Please enter the URL you were redirected to: ")
            authData = spotifyAuthObject.parse_response_code(authResult)
            authorization = spotifyAuthObject.get_access_token(authData)
        if(authorization):
            print("Successfully authorized Spotify credentials.")
            return authorization['access_token']

    def login():
        usernameInput = input('Enter username for authorization: ')


        return sutil.authenticate(usernameInput)

    def generateList():
        pass







sut = Sutify()
sut.run()


