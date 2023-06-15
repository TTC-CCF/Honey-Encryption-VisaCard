# https://github.com/danielzuot/honeyencryption
# credit_card_test.py


import DTE
import os
import sys


with open('bin.txt','r') as bin:
    prefixes = eval(bin.read())



credit_card_example = '4720030000000016'
secret_key = 2048197655563215
guess_key = 204197554


if (len(sys.argv)>1):
	credit_card_example=sys.argv[1]

if (len(sys.argv)>2):
	secret_key=int(sys.argv[2])

if (len(sys.argv)>3):
	guess_key=int(sys.argv[3])

print ("Credit card: "+credit_card_example )
print ("Secret key: "+str(secret_key))

print ("Guess key: "+str(guess_key))


credit_card_fxns = DTE.CreditCardProbabilityFxns(prefixes)


# Use DTE on credit card example
seed = DTE.encode(credit_card_example, credit_card_fxns)
if seed != -1:
    ciphertext = secret_key ^ seed
    decipher_seed = guess_key ^ ciphertext
    
    # print (seed, decipher_seed)
    print ("CIPHERTEXT: "+str(ciphertext))

    print ("HEX(SEED): "+str(hex(seed)))
    print ("HEX(GUESSED_SEED): "+str(hex(decipher_seed)))
    print ("")
    
    message = DTE.decode(decipher_seed, credit_card_fxns)
    print ("MESSAGE: "+message)