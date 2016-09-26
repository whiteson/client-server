# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013
import select, socket, sys, pdb
from pychat_util import Hall, Room, Player,IbeSetup, IBE
import pychat_util
import pickle
#from charm.toolbox.pairinggroup import PairingGroup
#import charm.schemes.ibenc.ibenc_bf01 as ibenc
print('this is the pychatutil', pychat_util)
READ_BUFFER = 4096
host = sys.argv[1] if len(sys.argv) >= 2 else ''
listen_sock = pychat_util.create_socket((host, pychat_util.PORT))
hall = Hall()
#upon initilization we will hold in memory mpk, msk,group and ibe-object
#mpk = IbeSetup.getmasterpublickey(Hall())
#msk = hall.getmastersecretkey()
#hall.ibeintialize()
connection_list = []
connection_list.append(listen_sock)
print ('this is hallibesetup', hall.ibesetup)
#picklestring = pickle.dumps(IbeSetup)

#with open('IbeSetup', 'wb') as output:
    #pickle.dump(group, output, pickle.HIGHEST_PROTOCOL)
    #pickle.dump(picklestring, output, -1)

while True:
    # Player.fileno()
    read_players, write_players, error_sockets = select.select(connection_list, [], [])
    for player in read_players:
        if player is listen_sock: # new connection, player is a socket
            new_socket, add = player.accept()
            new_player = Player(new_socket)
            connection_list.append(new_player)
            hall.welcome_new(new_player)
            #hall.sendmpk(new_player)
        else: # new message
            msg = player.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode().lower()
                hall.handle_msg(player, msg)
            else:
                player.socket.close()
                connection_list.remove(player)

    for sock in error_sockets: # close error sockets
        sock.close()
        connection_list.remove(sock)
