#!/usr/bin/env python3
"""Argparse type validators used by the lets-debug CLI."""
import argparse
import re

from typing import Any


class ValidateArgRegex:
    """Argparse `type=` callable that enforces a named regex pattern.

    Currently supports only the `domain` pattern: an optional `*.` wildcard
    prefix followed by one or more DNS labels and a 2+ character TLD.
    """

    patterns = {
        # Optional `*.` wildcard, then one or more labels (no leading hyphen),
        # then a 2+ character alphabetic TLD.
        'domain': re.compile(r'^(\*\.)?(?!-)[A-Za-z0-9-]+(\.(?!-)[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$'),
    }

    def __init__(self, argtype: Any) -> None:
        if argtype not in self.patterns:
            raise KeyError(f"{argtype} is not a supported argument pattern, choose from: {','.join(self.patterns)}")
        self._argtype = argtype
        self._pattern = self.patterns[argtype]

    def __call__(self, value: Any) -> Any:
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                f"'{value}' is not a valid argument - does not match {self._argtype} pattern")
        return value
