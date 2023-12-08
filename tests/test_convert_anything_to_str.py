#!/usr/bin/env python
# -*- coding: utf-8
# Possible test commands:
# PYTHONPATH=. python2 tests/test_convert_anything_to_str.py
# PYTHONPATH=. python3 tests/test_convert_anything_to_str.py
# python2 -m unittest discover
# python3 -m unittest discover
"""Test case for XSConsoleLang.convert_anything_to_str()"""
import os
import sys
import unittest

from XSConsoleLang import convert_anything_to_str


class TestIPAddress(unittest.TestCase):
    def test_convert_anything_to_str(self):
        expected_string = "Török"
        encoded_iso8859 = b'T\xf6r\xf6k'
        encoded_as_utf8 = b"T\xc3\xb6r\xc3\xb6k"

        assert expected_string == convert_anything_to_str(encoded_as_utf8)
        # GitHub's Python2 is apparently a custom build that is limited:
        if sys.version_info > (3, 0) or not os.environ.get("GITHUB_ACTION"):
            assert expected_string == convert_anything_to_str(encoded_iso8859, "iso-8859-1")

        if sys.version_info.major < 3:  # For Py2, on Py3, str == unicode
            unicode_str = encoded_as_utf8.decode("utf-8")
            assert str(type(unicode_str)) == "<type 'unicode'>"
            assert expected_string == convert_anything_to_str(unicode_str)

        assert expected_string == convert_anything_to_str(expected_string)

        # Special case for then call location check the result for None:
        assert convert_anything_to_str(None) == None

        # Test cases for str(arg)
        assert convert_anything_to_str(42) == "42"
        assert convert_anything_to_str(42.2) == "42.2"
        assert convert_anything_to_str(Exception("True")) == "True"
        assert convert_anything_to_str(True) == "True"
        assert convert_anything_to_str(False) == "False"


if __name__ == "__main__":
    unittest.main()
