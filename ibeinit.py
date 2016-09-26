from charm.toolbox.pairinggroup import PairingGroup
import charm.schemes.ibenc.ibenc_bf01 as ibenc
import json
import pickle
ibenc.debug = False
from charm.core.engine.util import objectToBytes,bytesToObject
from charm.core.math.integer import integer,serialize,deserialize
#serObject = mySerializeAPI()	
#pk_bytes = objectToBytes(pk, serObject)	
#orig_pk = bytesToObject(pk_bytes, serObject) 
from charm.core.engine.util import objectToBytes,bytesToObject

group = PairingGroup('MNT224') # assuming you're using the PBC pairing module
print(type(group))
t = 1,2,3
print ('This is a tuple {0}'.format(group))
print('this is the format group ', format(group)[1:4:2])


#pk_bytes = serialize(group)

#orig_pk = desirilize(group)

ibe = ibenc.IBE_BonehFranklin(group)
mpk, msk = ibe.setup()
print ('master secrete key: ', msk)
ID = "teste"
sk = ibe.extract(msk, ID)
print ('teste and secrete key: ', sk )
#message must have a valid width of  
m = b'12345678901234567890123456789012345678901234567890123456789123 5'
print('message', m)
ciphertext = ibe.encrypt(mpk, ID, m)
print('1', PairingGroup('MNT224'))
print('2', PairingGroup('MNT224'))
print('3', PairingGroup('MNT224'))
print('4', PairingGroup('MNT224'))
au= (group.serialize(ciphertext['U']))
aw = serialize(ciphertext['W'])
av= serialize(ciphertext['V'])
sk = objectToBytes(sk,group)
mpk = objectToBytes(mpk,group)	
print (au)
print (aw)
print (av)
print (sk)
print (type(au))
print (type(aw))
print (type(av))
print(type(mpk))

au= (group.deserialize(au))
aw = deserialize(aw)
av= deserialize(av)
sk = bytesToObject(sk, group) 
mpk = bytesToObject(mpk,group)	
print (au)
print (aw)
print (av)
print (sk)
print (mpk)
print (type(au))
print (type(aw))
print (type(av))
print(type(sk))
print(type(mpk))
ciphertext = {}
ciphertext['U'] = (au)
ciphertext['W'] = (aw)
ciphertext['V'] = (av)

orig_m = ibe.decrypt(mpk, sk, ciphertext)
print('original text', orig_m.decode("utf-8"))