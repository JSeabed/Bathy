import unittest

import sys
sys.path.append('../')

#import timer
import aml

#from unittest.mock import MagicMock
from mock import MagicMock

class Test_Aml(unittest.TestCase):

    def test_dummy(self):
        dummy = "0000.000  00.000  21.158  0001.534  008.07  00.000  0000.000  0000.00"
        expected_result = "$SBDAML,01-01-2000,02:17:02.722622,00.000,21.158,0001.534,008.07,00.000,0000.000,0000.00,st"

        aml.getTime = MagicMock(return_value="01-01-2000,02:17:02.722622")
        aml.getTime()

        result = aml.parseAml(dummy)

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
