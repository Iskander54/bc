from os.path import dirname, abspath
import sys
sys.path.insert(0,dirname(dirname(abspath(__file__))))
from transaction import Transaction
import unittest

class TransactionTest(unittest.TestCase):

    def test_(self):
        transaction = Transaction('Alex','Yann','signature',15)
        tx=transaction.to_ordered_dict()
        self.assertIsInstance(tx,dict)

unittest.main()