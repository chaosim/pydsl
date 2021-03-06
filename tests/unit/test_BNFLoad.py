#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2008-2013 Nestor Arocha

"""Test BNF file loading"""

import unittest
from pydsl.File.BNF import load_bnf_file
from pydsl.File.Python import load_python_file
from pydsl.Grammar.Definition import RegularExpression

class TestFileLoader(unittest.TestCase):
    """Loading a bnf instance from a .bnf file"""
    def testFileLoader(self):
        repository = {'integer':RegularExpression("^[0123456789]*$"), 
                'DayOfMonth':load_python_file('pydsl/contrib/grammar/DayOfMonth.py')}
        self.assertTrue(load_bnf_file("pydsl/contrib/grammar/Date.bnf", repository))
