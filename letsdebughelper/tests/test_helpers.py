#!/usr/bin/env python3
import argparse
import unittest

from parameterized import parameterized

from letsdebughelper.helpers import ValidateArgRegex


class TestHelpers(unittest.TestCase):

    @parameterized.expand([
        ('testdomain.com', 'testdomain.com'),
        ('.testdomain.com', '.testdomain.com'),
        ('*.testdomain.com', '*.testdomain.com'),
        ('sub-site.testdomain.com', 'sub-site.testdomain.com'),
        ('sub.sub.testdomain.com', 'sub.sub.testdomain.com'),
    ])
    def test_correct_validate_domain_arg_regex(self, domain, expected):
        """Helpers: Test correct domain regex"""
        actual = ValidateArgRegex('domain')(domain)
        self.assertEqual(actual, expected)

    def test_bad_validate_domain_arg_regex(self):
        """Helpers: Test bad domain regex"""
        domain = 'testdomainthatiswrong'
        with self.assertRaises(argparse.ArgumentTypeError):
            ValidateArgRegex('domain')(domain)

    def test_wrong_arg(self):
        """Helpers: Test bad domain regex"""
        domain = 'testdomainthatiswrong'
        with self.assertRaises(KeyError):
            ValidateArgRegex('wrong')(domain)
