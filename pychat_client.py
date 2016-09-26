import select, socket, sys
#from pychat_util import Room, Hall, Player, IBE, IbeSetup
import pychat_util
from pychat_util import *
#import pickle
#import marshal
from charm.toolbox.pairinggroup import PairingGroup
#import charm.schemes.ibenc.ibenc_bf01 as ibenc
group = PairingGroup('MNT224') # assuming you're using the PBC pairing module
#ibe = ibenc.IBE_BonehFranklin(group)
#add functionality for ibe 
#from charm.toolbox.pairinggroup import PairingGroup
#import charm.schemes.ibenc.ibenc_bf01 as ibenc
#group = PairingGroup('MNT224') # assuming you're using the PBC pairing module
ibe = ibenc.IBE_BonehFranklin(group)
#mpk, msk = ibe.setup()
from charm.core.engine.util import objectToBytes,bytesToObject
from charm.core.math.integer import integer,serialize,deserialize	
#serObject = mySerializeAPI()

READ_BUFFER = 4096
if len(sys.argv) < 2:
    print("Usage: Python3 client.py [hostname]", file = sys.stderr)
    sys.exit(1)
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], pychat_util.PORT))
def prompt():
    print('>', end=' ', flush = True)

print("Connected to server\n")
msg_prefix = ''
socket_list = [sys.stdin, server_connection]
x=''
name=''
secretkey=''
mpk=''
sk=''
#print(group)
print(socket_list)
#print('Server mpk:', IbeSetup.mpk)
#with open('IbeSetup', 'rb') as input:
#    company1 = pickle.load(input)
#    print(str(company1))
#global thekeys
#print('pairinggroup from utilities  ', pairinggroup)
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
    
while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_connection: # incoming message 
            msg = s.recv(READ_BUFFER)
            print (name)
            if not msg:
                print("Server down!")
                sys.exit(2)
            else:
                if msg == pychat_util.QUIT_STRING.encode():
                    sys.stdout.write('Bye\n')
                    sys.exit(2)
                else:
                    if (mpk=='' and name!=''):
                        
                        if (b'mpk') in msg[0:4]:
                            #print('mpk send all--->',group)
                            #print('mpk send all--->',msg)
                            mpk = bytesToObject(msg[3::1],group)
                            #print('we receive that master  public key', mpk)
                        else:
                            msg=b'givemethecredentials'
                        server_connection.sendall(msg)
                        

                    if(b'ski') in msg[0:4]:
                        #print('here we are at the ski')
                        print('this is the ski')
                        print('this is the message from: ', msg[3::1])
                        sk = bytesToObject(msg[3::1], group) 
                        print('Secret key intilized!!! secure messaging')
                        print('this is my sk :', sk)
                            
                        
                    if (b'<ibe') in msg[0:4]:
                        print('our msg is of type: ', type(msg))
                        print('the rs',read_sockets)
                        #print('this is the original message',msg)
                        ciphertext ={}
                        #msg = str(msg)
                        #msg = msg.split()[2:len(msg.split())]
                        msg = msg[5::1]
                        #print ('message before loop ',msg)
                        #msg.replace("", "<ibe> : ", 1)
                        #msg = msg.decode()
                        #msg = pickle.loads(msg[6::1])
                        #msg = msg[4::1]
                        firstcomma = find_nth(msg, b",", 1)
                        secondcomma = find_nth(msg, b",", 2)
                        au =msg[msg.find(b',')+5:secondcomma]
                        aw =msg[secondcomma+5:-1]
                        av = msg[msg.find(b':')+1:msg.find(b','):1]
                        #print ('au is here',au)
                        #print ('aw is here',aw)
                        #print ('av is here',av)
                        #print('71 line messageis ',msg)
                        #av = msg[0]  
                        #au = msg[1] 
                        #aw = msg[2]
                        au= group.deserialize(au)
                        aw = (deserialize(aw))
                        av= (deserialize(av))
                        #print(type(au))
                        #print(type(aw))
                        #print(type(av))
                        ciphertext['U']  = (au) 
                        ciphertext['W']  = (aw)
                        ciphertext['V'] = (av)
                        ct1= {}
                        ct1['U'] = au
                        ct1['V'] = av
                        ct1['W'] = aw
                        print ('This is my ciphertext for input', ct1)
                        #msg = dict((k,int(v)) for k,v in msg.items())
                        #msg = dict(item.split("=") for item in int(msg.split(";")))
                        #ori = 'class_="template_title" height="50" valign="bottom" width="535"'
                        #final = dict()
                        #for item in msg.split(';'):
                        #    pair = item.split('=')
                        #    final.update({pair[0] : list(map(int,pair[1][1:-1]))})
                        #msg = final
                        #print (msg)
                        #sk = secretkey
                        #print('mpk@sk@ciphertext - respectively:',mpk, sk, ct1)
                        msg = ibe.decrypt(mpk, sk, ct1)
                        if(msg!=None and type(msg)==bytes):
                            sys.stdout.write(msg.decode('utf-8'))
                        if (type(msg) == bytes):
                            server_connection.sendall(msg)
                        print (str(msg))
                        #server_connection.sendall(msg)
                        #msg = msg.encode()
                        #print('this is the msg:',msg)
                        #print('this is the final message:', msg.decode('utf-8'))
                        #msg = marshal.loads(msg)
                    else:    
                        sys.stdout.write(msg.decode())
                        if 'Please tell us your name' in msg.decode():
                            msg_prefix = 'name: ' # identifier for name
                        else:
                            msg_prefix = ''
                        prompt()

        else:
            msg = msg_prefix + sys.stdin.readline()
            if "name:" in msg:
                name = msg.split()[1]
                #mpk = IbeSetup.mpk
                #group = IbeSetup.group
                #ibe = IbeSetup.ibe
                #msk = IbeSetup.msk
                #intilize a new player with that name
                print("Intilized you IBE Scheme:", name)
                #x = IBE(name)
                #1print('This is  msk', msk)
                #sk = ibe.extract(msk, name)
                #print(type(sk))
                #print('this is my sk:',sk)
                #secretekey = sk
                #THis example below working but it initilazes again the mpk
                #x = pychat_util.IbeSetup()
                #print('Dictionary keyes :',x.thekeys)
                #print('end of the keyes')
                #print (x.ibeinitial(name))
                #print(x)
                #x.
                print('The user ID------> ',name)
                #print ('name for the ibe is ',x)
                #secretkey = x.extractsecretkey(name)
                #print ('the secrete key is ',secretkey)
                #mpk = x.getmasterpublickey()
                print('the master public key for the setup is:', mpk)
            server_connection.sendall(msg.encode())
