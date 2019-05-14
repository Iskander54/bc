from blockchain import Blockchain
from block import Block
from wallet import Wallet
import time

def timestamp_to_date(tstp):
    """ Function that convert timestamp to date """
    tick = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstp))
    #readable = time.ctime(1557684548)
    return tick

def get_miner(block):
    """ function that look for the miner of a block """
    for tx in block['transactions']:
        if tx['sender']=='MINING':
            return tx['recipient']
def dosearch(amount,sender,recipient,time,chaine):
    tmp=[]
    if(sender==None):
        pass
    else:
        for block in chaine:
            for tx in block['transactions']:
                if(tx['sender'].lower()==sender.lower()):
                    tmp.append(Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp'])))
        if tmp==[]:
            return tmp

    if(recipient==None):
        pass
    else:
        if(len(tmp)>0):
            tmpt=tmp
            tmp=[]
            for block in tmpt:
                    if(block.transaction['recipient'].lower()==recipient.lower()):
                        tmp.append(Search(block.block_index,block.transaction,block.miner,block.timestamp))
            if tmp==[]:
                return tmp

        else:
            for block in chaine:
                for tx in block['transactions']:
                    if(tx['recipient'].lower()==recipient.lower()):
                        tmp.append(Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp'])))
            if tmp==[]:
                return tmp
    
    if(amount==None):
        pass
    else:
        if(len(tmp)>0):
            tmpt=tmp
            tmp=[]
            for block in tmpt:
                if(float(block.transaction['amount'])==float(amount)):
                    tmp.append(Search(block.block_index,block.transaction,block.miner,block.timestamp))
            if tmp==[]:
                return tmp
        else:
            for block in chaine:
                for tx in block['transactions']:
                    print(tx['amount'],amount)
                    if(int(tx['amount'])==int(amount)):
                        tmp.append(Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp'])))
    return tmp

        
class Search():
    def __init__(self,block_index,transaction,miner,timestamp):
        self.block_index=block_index
        self.transaction=transaction
        self.miner=miner
        self.timestamp=timestamp



    def setup(chaine,recipient,amount,sender,time):
        """ Function that search tx in the blockchain """
        amount=None if amount==None else float(amount)
        founds=[]
        founds=dosearch(amount,sender,recipient,time,chaine)
        founds=founds.__dict__
        founds =[f.__dict__ for f in founds]
        """
        for search in founds:
            for tx in block['transactions']:
                field='amount'
                test = 1
                print(isinstance(test,float))
                print(isinstance(test,int))
                if (tx['sender']==sender or tx['sender']=='') and: 
                    wesh=timestamp_to_date(block['timestamp'])
                    print(wesh)
                    tmp=Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp']))
                    founds.append(str(tmp.__dict__))"""
        return founds





