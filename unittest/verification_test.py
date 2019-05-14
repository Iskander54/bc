from os.path import dirname, abspath
import sys
sys.path.insert(0,dirname(dirname(abspath(__file__))))
from verification import Verification
import unittest

class VerificationTest(unittest.TestCase):

    def setUp(self):
        self.transaction = Transaction('Alex','Yann','signature',15)

    def test_verify_transaction(self):
        tx=self.transaction.to_ordered_dict()
        self.assertIsInstance(tx,dict)

    def test_str(self):
        tx=self.transaction.__repr__()
        self.assertIsInstance(tx,str)

unittest.main()