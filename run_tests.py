#!/usr/bin/env python3
"""Roda toda a suíte de testes.

Uso:
    python3 run_tests.py

Equivalente a:
    python3 -m unittest discover -s tests -t .
"""
import sys
import unittest


def main():
    suite = unittest.TestLoader().discover("tests", top_level_dir=".")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
