from functools import reduce
import hashlib
import json
from block import Block
from transaction import Transaction
from wallet import Wallet
from common.utility import Utility

# The reward we give to miners (for creating a new block)
MINING_REWARD = 20
# path for data to be saved
FILE_PATH = 'data.json'


class BlockChain:
    def __init__(self, hosting_node_id):
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], 0, 0)
        # Initializing our (empty) blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.hosting_node = hosting_node_id

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, value):
        self.__chain = value

    def get_open_transactions(self):
        return self.__open_transactions

    def load_data(self):
        file_content = None
        try:
            file_content = Utility.json_read(FILE_PATH)
        except IOError:
            pass

        if file_content is not None:
            load_chain_from_file = []
            for block in file_content['blockchain']:
                converted_tx = [Transaction(
                    tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]

                load_chain_from_file.append(Block(block['index'], block['previous_hash'],
                                                  converted_tx, block['proof'], block['timestamp']))
            self.__chain = load_chain_from_file
            for tx in file_content['open_transactions']:
                self.__open_transactions.append(Transaction(
                    tx['sender'], tx['recipient'], tx['signature'], tx['amount']))

    def save_data(self):
        saveable_chain = [block.__dict__ for block in [Block(blk.index, blk.previous_hash, [tx.__dict__ for tx in blk.transactions], blk.proof, blk.timestamp)
                                                       for blk in self.__chain]]
        saveable_transactions = [
            tx.__dict__ for tx in self.__open_transactions]
        data_to_be_saved = {"blockchain": saveable_chain,
                            "open_transactions": saveable_transactions}
        Utility.json_save(FILE_PATH, data_to_be_saved)

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = Utility.generate_hash_for_given_block(last_block)
        proof = 0
        while not self.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        """Calculate and return the balance for a participant.

        Arguments:
            :participant: The person for whom to calculate the balance.
        """
        participant = self.hosting_node
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # Calculate the total amount of coins sent
        amount_sent = reduce(lambda total, currentItem: total +
                             sum(currentItem), [arr for arr in tx_sender if len(arr) > 0], 0)
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]

        # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
        # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        # Calculate the total amount of coins receive
        amount_received = reduce(lambda total, currentItem: total +
                                 sum(currentItem), [arr for arr in tx_recipient if len(arr) > 0], 0)

        # for tx in tx_recipient:
        #     if len(tx) > 0:
        #         amount_received += tx[0]

        # Return the total balance
        return amount_received - amount_sent

    def add_transaction(self, recipient, sender, signature, amount=1):
        """ Add transaction to open transaction.

        Arguments:
            :sender: the guy who is sending the money.
            :recipient: the guy who is receiving the money.
            :amount: money money money.
        """
        """ Verify transaction before adding to the open transaction"""
        transaction = Transaction(sender, recipient, signature, amount)
        if not self.verify_transaction(transaction, self.get_balance):
            print('You don\'t have sufficient balance.')
            return

        self.__open_transactions.append(transaction)
        self.save_data()

    def mine_block(self):
        """Create a new block and add open transactions to it."""
        # Fetch the currently last block of the blockchain
        last_block = self.__chain[-1]
        # Hash the last block (=> to be able to compare it to the stored hash value)
        hashed_block = Utility.generate_hash_for_given_block(last_block)
        # proof of work
        proof = self.proof_of_work()
        # Miners should be rewarded, so let's create a reward transaction

        # dictionary is unordered mapped key and value pair, so using OrderDict to guarantee order to avoid hashing difference
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD
        # }
        # reward_transaction = OrderedDict(
        #     [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        reward_transaction = Transaction(
            'MINING', self.hosting_node, '', MINING_REWARD)
        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if for some reason the mining should fail, we don't have the reward transaction stored in the open transactions
        copied_open_transactions = self.__open_transactions[:]

        for transaction in copied_open_transactions:
            if (Wallet.verify_transaction(transaction) == False):
                return False

        copied_open_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_open_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

# Verification methods
    def valid_proof(self, transactions, previous_hash, proof):
        guessHash = hashlib.sha256(
            str(str([tx.to_ordered_dict() for tx in transactions])+str(previous_hash)+str(proof)).encode()).hexdigest()
        return guessHash.startswith('8e')

    def verify_chain(self, blockchain):
        for (index, block) in enumerate(blockchain):
            if(index == 0):
                continue
            if(block.previous_hash != Utility.generate_hash_for_given_block(blockchain[index - 1])):
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    def verify_transaction(self, transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    def verify_transactions(self, open_transactions, get_balance):
        """Verifies all open transactions."""
        return all([self.verify_transaction(tx, get_balance, False) for tx in open_transactions])
