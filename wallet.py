from Crypto.PublicKey import RSA
import Crypto.Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
"""binascii to convert binary data to string"""
import binascii
from common.utility import Utility


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create(self):
        """Generate private and public key"""
        private_key_binary = RSA.generate(1024, Crypto.Random.new().read)
        # public ke is always part of private key,
        # it helps to verify signature generated using private key
        public_key_binary = private_key_binary.publickey()
        # To decode from binary to string
        # 1. Convert binary to hexadecimal ex. binascii.hexlify(private_key.exportKey(format='DER'))
        # 2. Then decode to string in ascii formation
        private_key, public_key = (binascii.hexlify(private_key_binary.exportKey(format='DER')).decode(
            'ascii'), binascii.hexlify(public_key_binary.exportKey(format='DER')).decode('ascii'))
        self.private_key = private_key
        self.public_key = public_key
        self.__save()

    def load(self):
        keys = Utility.json_read('wallet.json')
        self.private_key = keys['private_key']
        self.public_key = keys['public_key']

    def sign_transaction(self, sender, recipient, amount):
        key = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.private_key)))
        payload = SHA256.new(
            (str(sender)+str(recipient)+str(amount)).encode('utf8'))
        signature = key.sign(payload)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        key = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(transaction.sender)))
        payload = SHA256.new(
            (str(transaction.sender)+str(transaction.recipient)
             + str(transaction.amount)).encode('utf8'))
        return key.verify(payload,
                          binascii.unhexlify(transaction.signature))

    def __save(self):
        data_to_be_saved = {'private_key': self.private_key,
                            'public_key': self.public_key}
        Utility.json_save('wallet.json', data_to_be_saved)

    def serialize(self):
        return self.__dict__
