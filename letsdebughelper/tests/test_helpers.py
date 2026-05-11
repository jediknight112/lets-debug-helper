#!/usr/bin/env python3
import argparse
import unittest

from parameterized import parameterized

from letsdebughelper.helpers import ValidateArgRegex


class TestHelpers(unittest.TestCase):

    @parameterized.expand([
        ('testdomain.com',),
        ('*.testdomain.com',),
        ('sub-site.testdomain.com',),
        ('sub.sub.testdomain.com',),
        ('a.b.c.d.example.io',),
    ])  # type: ignore
    def test_valid_domain_arg_regex(self, domain: str) -> None:
        """Helpers: domain regex accepts well-formed names."""
        self.assertEqual(ValidateArgRegex('domain')(domain), domain)

    @parameterized.expand([
        ('.testdomain.com',),     # leading dot
        ('testdomain.',),         # trailing dot, missing TLD
        ('-leading.com',),        # leading hyphen in label
        ('nodot',),               # no TLD separator
        ('example.c',),           # TLD too short
        ('exa mple.com',),        # whitespace
    ])  # type: ignore
    def test_invalid_domain_arg_regex(self, domain: str) -> None:
        """Helpers: domain regex rejects malformed names."""
        with self.assertRaises(argparse.ArgumentTypeError):
            ValidateArgRegex('domain')(domain)

    def test_unsupported_pattern_name(self) -> None:
        """Helpers: constructing with an unknown pattern name raises KeyError."""
        with self.assertRaises(KeyError):
            ValidateArgRegex('wrong')
