#!/usr/bin/python
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
from pydsl.Parser.LL import LL1RecursiveDescentParser

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"



from pydsl.contrib.bnfgrammar import *
from pydsl.Parser.Backtracing import BacktracingErrorRecursiveDescentParser
from pydsl.Parser.Weighted import WeightedParser
from pydsl.Parser.LR0 import LR0Parser
from pydsl.Lex import EncodingLexer
import unittest

class TestBacktracingRecursiveDescentParser(unittest.TestCase):
    @unittest.skip
    def testRecursiveLeftRecursion(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionsetlr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testRightRecursion(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionsetrr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testCenterRecursion(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionsetcr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testRecursiveDescentParserStore(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionset1)
        result = descentparser(string1)
        self.assertTrue(result)

    def testRecursiveDescentParserBad(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionset1)
        result = descentparser(string2)
        self.assertFalse(result)

    def testRecursiveDescentParserNull(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionset2)
        result = descentparser(string3)
        self.assertTrue(result)

    def testRecursiveDescentParserNullBad(self):
        descentparser = BacktracingErrorRecursiveDescentParser(productionset2)
        result = descentparser(string4)
        self.assertFalse(result)


class TestLR0Parser(unittest.TestCase):
    def testLR0ParseTable(self):
        """Tests the lr0 table generation"""
        from pydsl.Parser.LR0 import _slr_build_parser_table, build_states_sets
        state_sets = build_states_sets(productionset0)
        self.assertEqual(len(state_sets), 5)
        #1 . EI: : . exp $ , 
        #   exp : .SR
        #       transitions: S -> 3,
        #2 EI:  exp . $ ,
        #       transitions: $ -> 4
        #3 exp:  S . R,
        #       transitions: R -> 5
        #4 EI: exp $ .
        #5 exp:  S R .

        parsetable = _slr_build_parser_table(productionset0)
        print(parsetable)
        #self.assertEqual(len(parsetable), 3)


    def testLR0ParserStore(self):
        parser = LR0Parser(productionset0)
        tokelist = [x for x in EncodingLexer('utf8')(p0good)]
        result = parser.check(tokelist)
        self.assertTrue(result)

    @unittest.skip
    def testLR0ParserBad(self):
        parser = LR0Parser(productionset1)
        result = parser(string2)
        self.assertFalse(result)



class TestWeightedParser(unittest.TestCase):
    @unittest.skip
    def testWeightedLeftRecursion(self):
        parser = WeightedParser(productionsetlr)
        result = parser(dots)
        self.assertTrue(result)


    def testWeightedRightRecursion(self):
        parser = WeightedParser(productionsetrr)
        result = parser(dots)
        self.assertTrue(result)

    def testWeightedCenterRecursion(self):
        descentparser = WeightedParser(productionsetcr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testWeightedParserStore(self):
        parser = WeightedParser(productionset1)
        result = parser(string1)
        self.assertTrue(result)
        self.assertTrue(parser([x for x in string1]))

    def testWeightedParserBad(self):
        parser = WeightedParser(productionset1)
        result = parser(string2)
        self.assertFalse(result)

    def testWeightedParserNull(self):
        parser = WeightedParser(productionset2)
        result = parser(string3)
        self.assertTrue(result)

    def testWeightedParserNullBad(self):
        parser = WeightedParser(productionset2)
        result = parser(string4)
        self.assertFalse(result)

    @unittest.skip
    def testMixResults(self):
        from pydsl.Parser.Weighted import mix_results
        from pydsl.Tree import ParseTree
        from pydsl.Grammar.Symbol import NullSymbol
        result1 = ParseTree(0, 3, [NullSymbol()], "", None)
        result2 = ParseTree(0, 5, [NullSymbol()], "", None)
        result3 = ParseTree(3, 6, [NullSymbol()], "", None)
        result4 = ParseTree(6, 8, [NullSymbol()], "", None)
        result5 = ParseTree(7, 8, [NullSymbol()], "", None)
        set1 = [result1, result2]
        set1b = [set1]
        set2 = [result3]
        set2b = [set2]
        set3 = [result4, result5]
        set3b = [set3]
        result = mix_results([set1b, set2b, set3b], None)
        #TODO: check result
        self.assertTrue(len(result) == 1)
        


class TestLL1RecursiveDescentParser(unittest.TestCase):
    @unittest.skip
    def testRecursiveLeftRecursion(self):
        descentparser = LL1RecursiveDescentParser(productionsetlr)
        result = descentparser(dots)
        self.assertTrue(result)

    def testRightRecursion(self):
        descentparser = LL1RecursiveDescentParser(productionsetrr)
        self.assertRaises(Exception, descentparser,dots) #Ambiguous grammar

    def testCenterRecursion(self):
        descentparser = LL1RecursiveDescentParser(productionsetcr)
        self.assertRaises(Exception, descentparser,dots) #Ambiguous grammar

    def testLL1RecursiveDescentParserStore(self):
        descentparser = LL1RecursiveDescentParser(productionset1)
        result = descentparser(string1)
        self.assertTrue(result)

    def testLL1RecursiveDescentParserBad(self):
        descentparser = LL1RecursiveDescentParser(productionset1)
        result = descentparser(string2)
        self.assertFalse(result)

@unittest.skip
class TestPEGParser(unittest.TestCase):
    def testBasicChoice(self):
        from pydsl.Grammar.Alphabet import Choice
        from pydsl.Tree import ParseTree
        from pydsl.Parser.PEG import PEGParser
        gd = Choice([String('a'), String('b')])
        parser = PEGParser(gd)
        result = parser('a')
        self.assertTrue(isinstance(result, ParseTree))
