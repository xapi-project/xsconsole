import unittest

from XSConsoleData import Data


class TestDataIntegration(unittest.TestCase):

    def test_data_collection(self):
        '''Note that this will touch the filesystem.
        '''
        instance = Data().Inst()
        self.assertFalse(instance is None)


if __name__ == '__main__':
    unittest.main()
