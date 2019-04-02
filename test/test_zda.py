import unittest

import sys
sys.path.append('../')

#import timer
import zda

#from unittest.mock import MagicMock
from mock import MagicMock

class Test_Aml(unittest.TestCase):

    def test_dummy(self):

        pass
        # aml.getTime = MagicMock(return_value="01-01-2000,02:17:02.722622")
        # aml.getTime()

        # result = aml.parseAml(dummy)

        # self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
