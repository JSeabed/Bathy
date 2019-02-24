import unittest

import sys
sys.path.append('../')

#import aml
import timer

class Test_Aml(unittest.TestCase):

    def test_dummy(self):
        dummy = "0000.000  00.000  21.158  0001.534  008.07  00.000  0000.000  0000.00"

        result = timer.parseAml(dummy)

        self.assertEqual()

if __name__ == '__main__':
    unittest.main()
