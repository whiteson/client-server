# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013
import socket, pdb
#pickle use to serialize the data into the socket
#import pickle
#import json
import pickle
#import cPickle as pickle
#import io
#import marshal
#add functionality for ibe 
from charm.toolbox.pairinggroup import PairingGroup
import charm.schemes.ibenc.ibenc_bf01 as ibenc
#ibe = ibenc.IBE_BonehFranklin(group)
#mpk, msk = ibe.setup()
#mpk = self.mpk
#mpk = self.mpk
from charm.core.engine.util import objectToBytes,bytesToObject
from charm.core.math.integer import integer,serialize,deserialize
#serObject = mySerializeAPI()
#serialize(self, charm_object)
#deserialize(self, object)
#pk_bytes = objectToBytes(pk, group)	
#orig_pk = bytesToObject(pk_bytes, group)   
#serObject = mySerializeAPI()	
#pk_bytes = objectToBytes(pk, serObject)	
#orig_pk = bytesToObject(pk_bytes, serObject)

MAX_CLIENTS = 30
PORT = 22222
QUIT_STRING = '<$quit$>'
activeplayers = [1, 2, 3]
def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

thekeys={}

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

class Hall:  
    def __init__(self):
        #initialize only once the setup group @ ibe @ mpk @msk
        self.ibesetup = IbeSetup()
        global pairinggroup
        pairinggroup = self.ibesetup
        ibesetup = self.ibesetup
        print('Dictionary keyes :',thekeys)
        print('end of the keyes')
        print('master public key is:',ibesetup.mpk)
        print('master secret key is:',ibesetup.msk)
        print(' ibe is:',ibesetup.ibe)
        print('group is:',ibesetup.group)
        #var = secretekey(ibesetup)
        #var2 = IBE(ibesetup)
        print(ibesetup.mpk)
        self.ibesetup = ibesetup
        #print(var,var2)
        #create a initial sk extraxtion  function for player name
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}
        #self.ibe_setup = {} # {keys: values}
        #self.group = PairingGroup('MNT224') # assuming you're using the PBC pairing module
        #self.ibe = ibenc.IBE_BonehFranklin(self.group)
        ##self.mpk, self.msk = self.ibe.setup()
        #group = self.group
        #mpk=self.mpk
        #msk=self.msk
        #ibe = self.ibe
        
    #def sendkeys(self,)
    def welcome_new(self, new_player):
        new_player.socket.sendall(b'Welcome to pychat with IBE.\nPlease tell us your name:\n')
        #self.getibeobject()
        #mpk = self.getmasterpublickey()
    def sendmpk(self, new_player):
        self.mpk = objectToBytes(ibesetup.mpk,ibesetup.group)
        
        print ('this is the mpk:that goes to the client', self.mpk)
        new_player.socket.sendall(b'<mpk>' + self.mpk)

    def list_rooms(self, player):
        
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'
            player.socket.sendall(msg.encode())
        else:
            msg = 'Listing current rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            player.socket.sendall(msg.encode())       
            
    def get_name(self, player):
        return player.name  

    def handle_msg(self, player, msg):
        
        instructions = b'Instructions:\n'\
            + b'[<list>] to list all rooms\n'\
            + b'[<join> room_name] to join/create/switch to a room\n' \
            + b'[<manual>] to show instructions\n' \
            + b'[<player>] to show the list of players\n' \
            + b'[<ibe>] name message (Send identity basedencrypted message from a room)\n' \
            + b'[<quit>] to quit\n' \
            + b'Otherwise start typing and enjoy!' \
            + b'Use the word ski to get your sk before ibe!' \
            + b'\n'

        print(player.name + " says: " + msg)
        
        if "name:" in msg:
            name = msg.split()[1]
            #intilize a new player with that name
            player.name = name
            print("New connection from:", player.name)
            player.socket.sendall(instructions)
            
            
        elif "givemethecredentials" in msg:
            print (b'mpk', self.ibesetup.mpk)
            mpk = objectToBytes(self.ibesetup.mpk,self.ibesetup.group)
            player.socket.sendall(b'mpk'+mpk)
            
        elif "ski" in msg:
            testsk = self.ibesetup.ibe.extract(self.ibesetup.msk, player.name)
            testsk = objectToBytes(testsk,self.ibesetup.group)
            #player.socket.sendall(b'One minute we intilize your secrete key')
            print('secret key for player is ', testsk)
            print("New connection from:", player.name)
            #Create his secret kety and send it serialized sk
            player.socket.sendall(b'ski'+testsk)
            #player.socket.sendall(instructions)
            
        
            
        elif "<ibe>" in msg:
            
            secondnull = find_nth(msg, " ", 2)
            playernameto = msg.split()[1]
            if(msg.split()[2]!=''):
                content = msg[secondnull::1]
            mpk = self.ibesetup.mpk
            print('this is the mpk from ibe handle message', mpk)
            ibe = self.ibesetup.ibe
            group = self.ibesetup.group
            print('The receiver of this message is :',playernameto)
            print('And the message is :',msg)
            if player.name in self.room_player_map:
                self.rooms[self.room_player_map[player.name]].broadcastEnc(group,mpk,ibe, player, content,playernameto)
                for keys,values in self.room_player_map.items():
                    #print(keys)
                    print(self.room_player_map[player.name])

        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2: # error check
                room_name = msg.split()[1]
                if player.name in self.room_player_map: # switching?
                    if self.room_player_map[player.name] == room_name:
                        player.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else: # switch
                        old_room = self.room_player_map[player.name]
                        self.rooms[old_room].remove_player(player)
                if not same_room:
                    if not room_name in self.rooms: # new room:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].players.append(player)
                    self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player.name] = room_name
            else:
                player.socket.sendall(instructions)

        elif "<list>" in msg:
            self.list_rooms(player)
        
        elif "<player>" in msg:
            if len(msg.split()) >= 2: # error check
                playername = msg.split()[1]
            msg = self.name + " welcomes: " + from_player.name + '\n'
            for player in self.players:
                player.socket.sendall(msg.encode())

        elif "<manual>" in msg:
            player.socket.sendall(instructions)
        
        elif "<quit>" in msg:
            player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        else:
            # check if in a room or not first
            if player.name in self.room_player_map:
                self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
                for keys,values in self.room_player_map.items():
                    print(keys)
                    print(self.room_player_map[player.name])
                #ID = 'john'
                #m=b'nikos'
                #ct = ibe.encrypt(mpk, ID, m)
                #msg = msg + sth.decode('utf-8')
                #self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [<list>] to see available rooms! \n' \
                    + 'Use [<join> room_name] to join a room! \n'
                player.socket.sendall(msg.encode())
    
    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Player: " + player.name + " has left\n")
        player.socket.sendall(player.name)
        #return player.name
        
    def ibe(self,ID):
        self.sk = ibe.extract(msk, ID)
        self.playersname.append(ID)
        sk = ibe.extract(msk, ID)
        for keys,values in sk.items():
            print(keys)
            print(values)
        return sk
        
    
class Room:
    def __init__(self, name):
        self.players = [] # a list of sockets
        self.name = name

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n'
        for player in self.players:
            player.socket.sendall(msg.encode())
    
    def broadcastEnc(self,group, mpk,ibe, from_player, content, playernameto):
        #msg = msg.decode()
        #print (msg)
        #msg = msg.split()[2:len(msg.split())]
        #msg = marshal.dumps(str(msg),-1)
        content = content.encode()
        #msg = pickle.dumps(msg,-1)
        print ('encoded message', content)
        print ('master publix key @player name @ final@ message: ',mpk,playernameto,content)
        ciphertext  = ibe.encrypt(mpk, playernameto, content)
        print (ciphertext)
        au= (group.serialize(ciphertext['U']))
        aw = serialize(ciphertext['W'])
        av= serialize(ciphertext['V'])
        
        #print ('au is here',au)
        #print ('aw is here',aw)
        #print ('av is here',av)
        
        
        #msg = ciphertext.items()
        msg = b'<ibe>'+b'{'b'"V":'+av+b',"U":'+au+b',"W":'+aw+b'}'
        #alist = []
        #alist.insert(0,av)
        #alist.insert(1,au)
        #alist.insert(2,aw)
        #msg = str( 'V='+ str(ciphertext["V"]) +';'+ 'U='+str(ciphertext["U"]) +';'+ 'W='+str(ciphertext["W"]))
        #Parsing data throu locals and build up the dictionary  again for the receiver
        #>>> mydict = {'raw': 'data', 'code': 500}
        #>>> locals().update(mydict)
        #print (msg)
        #msg = pickle.dumps(msg)
        #print (msg)
        #msg = msg.encode()
        #msg = pickle.loads(msg)
        #print (msg)
        #msg = msg.serialize()
        #msg = pickle.dumps(str(ciphertext),-1)
        #msg = io.StringIO(msg)
        #msg = pickle.dumps(msg,-1)
        #msg = marshal.dumps(str(msg),-1)
        #msg =au + av  + aw 
        #msg = b"<ibe>"+ msg
        #msg = slice(au,aw,av)
        print (msg)
        #alist =b'<ibe> ' +  pickle.dumps(alist,-1)
        #print(alist)
        #msg =alist
        print(msg)
        #msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            player.socket.sendall(msg)
            
            
    def broadcastDec(self, from_player, msg, playernameto):
        msg = msg.decode()
        print (msg)
        msg = msg.split()[2:len(msg.split())]
        print (msg)
        msg = marshal.dumps(str(msg),-1)
        print (msg)
        msg = ibe.encrypt(mpk, playernameto, msg)
        print (msg)
        msg = marshal.dumps(str(msg),-1)
        print (msg)
        msg = b"<ibe> "+ b": "+msg
        #msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            player.socket.sendall(msg)
            
    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            player.socket.sendall(msg)

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode() + b"has left the room\n"
        self.broadcast(player, leave_msg)

class Player:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()

class IbeSetup():
    group = PairingGroup('MNT224') # assuming you're using the PBC pairing module
    #with open('keys.txt', 'wb') as output:
     #       #pickle.dump(group, output, pickle.HIGHEST_PROTOCOL)
      #      pickle.dump(format(group), output, -1)

    #with open('keys.txt', 'rb') as input:
     #   company1 = pickle.load(input)
      #  print(company1)
    ibe = ibenc.IBE_BonehFranklin(group)
    mpk, msk = ibe.setup()
    def __init__(self):
        global thekeys
        thekeys={}
        self.group = IbeSetup.group # assuming you're using the PBC pairing module
        self.ibe = IbeSetup.ibe
        self.mpk = IbeSetup.mpk
        self.msk = IbeSetup.msk
        print('Initiliazed')
        self.masterpublic = self.mpk
        #Create a new instance and pass the variables to IBE
        #createplayer = IBE(self.group,self.ibe,self.mpk,self.msk)
        thekeys['group1'] = self.group
        thekeys['ibe1'] = self.ibe
        thekeys['mpk1'] = self.mpk
        thekeys['msk1'] = self.msk
    
    
    def extractsecretkey(self,name):
        print (thekeys)
        #self.ibe = Hall.ibe
        #self.msk = Hall.msk
        ibe = thekeys['ibe1']
        msk = thekeys['msk1']
        #self.playersname.append(ID)
        self.sk = ibe.extract(msk, name)
        for keys,values in self.sk.items():
            print(keys)
            print(values)
        return self.sk
        
        
    def getibe(self):
        print(self.ibe)
        return self.ibe
        
    def getmasterpublickey(self):
        print(self.mpk)
        return self.mpk
        
    def getmastersecretkey(self):
        print(self.msk)
        return self.msk

class IBE():    
    def __init__(self,name):
        global thekeys
        self.playersname = []#a listof players with ibe
        self.named=name
        self.thekeys = IbeSetup.thekeys  
        #global group1,ibe1,mpk1,msk1
        #msk = ibesetup.getmasterpublickey()
        #ibesetup = self.IbeSetup.(var)
        #sk = self.IbeSetup.(var)
        #print (mpk1)
        #self.ibe = Hall.ibe
        #self.mpk = mpk1
        #self.msk = Hall.msk
        #print('name from IBE class:',  name)
        print('the keyes:',  thekeys)
        
    def ibeinitial(self,ID):
        global thekeys
        print (thekeys)
        #self.ibe = Hall.ibe
        #self.msk = Hall.msk
        ibe = thekeys['ibe1']
        msk = thekeys['msk1']
        self.playersname.append(ID)
        self.sk = ibe.extract(msk, ID)
        for keys,values in self.sk.items():
            print(keys)
            print(values)
        return self.sk
               
       

