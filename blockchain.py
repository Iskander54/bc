import functools
import hashlib
import json
import pickle
import requests
from os.path import dirname, abspath

from utility.hash_util import hash_block,hash_string_256
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet
# The reward we give to miners (for creating a new block)
MINING_REWARD = 10
print(__name__)
pwd=dirname(dirname(abspath(__file__)))

class Blockchain:
    def __init__(self,public_key,node_id):
        genesis_block = Block(0,'',[],100,0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.__peer_nodes = set()
        self.node_id = node_id
        self.public_key = public_key
        self.resolve_conflicts = False
        self.load_data()
    
        


    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self,val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

        
    def load_data(self):
        try:
            with open('{}blockchain-{}.txt'.format('blockchain/',self.node_id)
            ,mode='r') as f:
                # file_content = pickle.loads(f.read())
                file_content = f.readlines()
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot'] 
                updated_blockchain=[]
                blockchain = json.loads(file_content[0][:-1])
                for block in blockchain:
                    converted_tx= [Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount']) for tx in block['transactions']]
                    updated_block=Block(block['index'],block['previous_hash'],converted_tx,block['proof'],block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.__chain=updated_blockchain
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction= Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError,IndexError):
            print('Handled Exception...')
        



    def save_data(self):
        try :
            with open('{}blockchain-{}.txt'.format('blockchain/',self.node_id),mode='w') as f:
                saveable_chain = [block.__dict__.copy() for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],block_el.proof,block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed')


    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash=hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof +=1
        return proof



    def get_balance(self,sender=None):
        """Calculate and return the balance for a participant.

        Arguments:
            :participant: The person for whom to calculate the balance.
        """
        if sender == None:
            if self.public_key == None:
                return None
            participant=self.public_key
        else :
            participant = sender
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
        # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # Return the total balance
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]
# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]


    def add_transaction(self,recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
    #  transaction = {
    #     'sender': sender,
        #    'recipient': recipient,
        #   'amount': amount
        #}
        #if self.public_key == None:
        #    return False
        transaction = Transaction(sender,recipient,signature,amount)
        if not Wallet.verify_transaction(transaction):
            return False
        if Verification.verify_transaction(transaction,self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url,json={'sender':sender, 'recipient':recipient,'amount':amount,'signature':signature})
                        if response.status_code == 400 or response.status_code == 500: 
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False


    def mine_block(self):
        """Create a new block and add open transactions to it."""
        # Fetch the currently last block of the blockchain
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        # Hash the last block (=> to be able to compare it to the stored hash value)
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # Miners should be rewarded, so let's create a reward transaction
        #reward_transaction = {
        #    'sender': 'MINING',
        #    'recipient': owner,
        #    'amount': MINING_REWARD
        #}
        reward_transaction = Transaction('MINING', self.public_key,'',MINING_REWARD)
        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if for some reason the mining should fail, we don't have the reward transaction stored in the open transactions
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block =  Block(len(self.__chain),hashed_block,copied_transactions,proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions']= [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url,json={'block':converted_block})
                if response.status_code == 400 or response.status_code == 500: 
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self,block):
        transactions = [Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'],block['proof'])
        hashes_match =hash_block(self.chain[-1])==block['previous_hash']
        print('hashes_match : {} -- proof is valid = {} '.format(hashes_match,proof_is_valid))
        if not proof_is_valid or not hashes_match:
            return False
        converted_block=Block(block['index'],block['previous_hash'],transactions, block['proof'],block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient ==itx['recipient'] and opentx.amount==itx['amount'] and opentx.signature==itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print(' Item was already removed')
        self.save_data()
        return True
    

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try :
                response = requests.get(url)
                node_chain = response.json() 
                node_chain = [Block(block['index'], block['previous_hash'],block['transactions'],block['proof'],block['timestamp']) for block in node_chain]
                for block in node_chain:
                    block.transactions=[Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount']) for tx in block.transactions]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length>local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain=node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
            self.resolve_conflicts=False
            self.chain=winner_chain
            if replace:
                self.__open_transactions = []
            self.save_data()
            return replace

    def add_peer_node(self,node):
        """ adds a new node to the peer node set"""
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self,node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)