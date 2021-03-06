#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This file is part of pydsl.
#
#pydsl is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pydsl is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pydsl.  If not, see <http://www.gnu.org/licenses/>.


"""Tests the Grammar definition instances"""


__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2014, Nestor Arocha"
__email__ = "nesaro@gmail.com"

import unittest
from pydsl.Grammar.Definition import String
from pydsl.Alphabet import Encoding
from pydsl.Alphabet import Alphabet


@unittest.skip
class TestGrammarDefinitionPLY(unittest.TestCase):
    def setUp(self):
        import plye
        from pydsl.Grammar.Definition import PLYGrammar
        self.grammardef = PLYGrammar(plye)

    @unittest.skip
    def testEnumerate(self):
        self.grammardef.enum()

    @unittest.skip
    def testFirst(self):
        self.grammardef.first

    @unittest.skip
    def testMin(self):
        self.grammardef.minsize

    @unittest.skip
    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet, Alphabet)

class TestGrammarDefinitionJson(unittest.TestCase):
    def setUp(self):
        from pydsl.Grammar.Definition import JsonSchema
        self.grammardef = JsonSchema({})

    def testEnumerate(self):
        self.assertRaises(NotImplementedError, self.grammardef.enum)

    def testFirst(self):
        self.grammardef.first

    def testMin(self):
        self.grammardef.minsize

    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertEqual(self.grammardef.alphabet, Encoding('ascii'))

