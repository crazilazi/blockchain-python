from time import time
from common.print import Print


class Block(Print):
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time

    def serialize(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': [tx.serialize() for tx in self.transactions],
            'proof': self.proof,
            'timestamp': self.timestamp
        }
