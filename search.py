from blockchain import Blockchain
from block import Block
from wallet import Wallet
import time
import json

def timestamp_to_date(tstp):
    """ Function that convert timestamp to date AAAA-MM-DD """
    tick = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstp))
    #readable = time.ctime(1557684548)
    return tick

def get_miner(block):
    """ function that look for the miner of a block """
    for tx in block['transactions']:
        if tx['sender']=='MINING':
            return tx['recipient']


def dosearch(amount,sender,recipient,time,chaine):
    """ Research algorithm"""
    tmp=[]
    #First checking the date because it is the high level of searching
    
    if(time==None):
        pass
    else:
        j=''
        for block in chaine:
            wrk=timestamp_to_date(block['timestamp']).split(' ')
            wrk_tmp=wrk[0].split('-')
            date=wrk_tmp[0]+wrk_tmp[1]+wrk_tmp[2]
            if(date==str(time)):
                for tx in block['transactions']:
                    tmp.append(Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp'])))
        #if research not found, return empty set
        if tmp==[]:
            return tmp

    #then criteria within the block
    if(amount==None):
        pass
    else:
        #if there is precedent criteria and is found check in the subset of block
        if(len(tmp)>0):
            tmpt=tmp
            tmp=[]
            for block in tmpt:
                if(float(block.transaction['amount'])==float(amount)):
                    tmp.append(Search(block.block_index,block.transaction,block.miner,block.timestamp))
            if tmp==[]:
                return tmp
        #or check in the entire blockchian if no former criteria or findings
        else:
            for block in chaine:
                for tx in block['transactions']:
                    print(tx['amount'],amount)
                    if(int(tx['amount'])==int(amount)):
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
    
    if(sender==None):
        pass
    else:
        if(len(tmp)>0):
            tmpt=tmp
            tmp=[]
            for block in tmpt:
                    if(block.transaction['sender'].lower()==sender.lower()):
                        tmp.append(Search(block.block_index,block.transaction,block.miner,block.timestamp))
            if tmp==[]:
                return tmp

        else:
            for block in chaine:
                for tx in block['transactions']:
                    if(tx['sender'].lower()==sender.lower()):
                        tmp.append(Search(block['index'],tx,get_miner(block),timestamp_to_date(block['timestamp'])))
            if tmp==[]:
                return tmp


    return tmp

        
class Search():
    """ Create an instance of the result of a research """
    def __init__(self,block_index,transaction,miner,timestamp):
        self.block_index=block_index
        self.transaction=transaction
        self.miner=miner
        self.timestamp=timestamp



    def setup(chaine,recipient,amount,sender,time):
        """ Function that operate the search tx in the blockchain """
        amount=None if amount==None else float(amount)
        founds=[]
        founds=dosearch(amount,sender,recipient,time,chaine)
        founds =[f.__dict__ for f in founds]
        return founds
