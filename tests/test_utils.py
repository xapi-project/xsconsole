import unittest

from XSConsoleUtils import IPUtils


class TestIPAddress(unittest.TestCase):

    def test_typical(self):
        self.assertTrue(IPUtils.ValidateIP('192.168.0.1'))

    def test_min(self):
        self.assertTrue(IPUtils.ValidateIP('0.0.0.1'))

    def test_beyond_min(self):
        self.assertFalse(IPUtils.ValidateIP('0.0.0.0'))

    def test_max(self):
        self.assertTrue(IPUtils.ValidateIP('255.255.255.255'))

    def test_beyond_max(self):
        self.assertFalse(IPUtils.ValidateIP('256.256.256.256'))


if __name__ == '__main__':
    unittest.main()
