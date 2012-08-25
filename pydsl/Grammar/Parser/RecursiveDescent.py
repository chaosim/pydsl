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

"""Recursive descent parser"""

__author__ = "Nestor Arocha Rodriguez"
__copyright__ = "Copyright 2008-2012, Néstor Arocha Rodríguez"
__email__ = "nesaro@gmail.com"

import logging
LOG = logging.getLogger(__name__)
from .Parser import TopDownParser, terminal_symbol_consume
from ..Tree import ParseTree
from pydsl.Abstract import TypeCheckList


#Los errores se almacenan aparte. Si otra alternativa cubre el error, se descarta,
#si no, se decide cual de las alternativas cubre mas texto y se presenta esa
#Errors are stored elsewhere. If another alternative covers this error, we discard this alternative.
#If not, we choose the alternative which covers more ammount of input

class RecursiveDescentResultTree:
    """Clase que almacena los resultados de la evaluacion de alternativas dentro del recursive decent parser. 
    Solo se usa a nivel interno
    Stores alternatives generated by the parser. Internal use only
    """
    def __init__(self, content):
        if content != None and not isinstance(content, ParseTree):
            raise TypeError
        self.content = content
        self.children = []

    def get_all(self):
        result = [self.content]
        for x in self.children:
            result += x.get_all()
        return result
    
    def get_lists(self):
        result = []
        mylist = [self.content]
        if not self.children and self.content:
            return [mylist]
        for child in self.children:
            x = child.get_lists()
            for li in x:
                assert(isinstance(li, list))
                if self.content == None:
                    result.append(li)
                else:
                    if self.content.rightpos == li[0].leftpos or self.content.rightpos == self.content.leftpos:
                        result.append(mylist + li)
                    else:
                        pass
        return result

    def append(self, content, startpos):
        if not isinstance(content, ParseTree):
            raise TypeError
        if self.content == None and startpos == 0:
            self.children.append(RecursiveDescentResultTree(content))
            return True
        elif not self.children and self.content.rightpos == startpos:
            self.children.append(RecursiveDescentResultTree(content))
            return True
        elif content.rightpos == content.leftpos and self.content != None and self.content.rightpos == startpos:
            self.children.append(RecursiveDescentResultTree(content))
            return True
        elif self.content != None and self.children and startpos == self.content.rightpos and content.rightpos != content.leftpos:
            self.children.append(RecursiveDescentResultTree(content))
            return True
        elif self.children:
            exito = False
            for x in self.children:
                if x.append(content, startpos):
                    exito = True
            return exito
        elif content == self.content:
            LOG.debug("duplicated content")
            return False
        else:
            #TODO:Raise an exception? 
            return False

    def last_poss(self):
        result = []
        if self.content:
            result.append(self.content.rightpos)
        for x in self.children:
            result += x.last_poss()
        if len(result) == 0:
            result = [0]
        return result


class RecursiveDescentParser(TopDownParser):
    """Recursive descent parser class"""
    #TODO: Should test recursion
    def get_trees(self, data, showerrors:bool = False) -> list:
        """ returns a SymbolTokenTree with best guesses """
        #import pdb
        #pdb.set_trace()
        LOG.debug("get_trees: data: " + str(data))
        LOG.debug("get_trees: _productionset.productionrulelist: " + str(self._productionset))
        if not isinstance(data, str):
            data = str(data).strip()
        result = self.__recursive_parser(self._productionset.initialsymbol, data, self._productionset.main_production, showerrors)
        finalresult = []
        for eresult in result:
            if eresult.leftpos == 0 and eresult.rightpos == len(data) and eresult not in finalresult:
                finalresult.append(eresult)        
        return finalresult

    def __recursive_parser(self, onlysymbol, data, production, showerrors:bool = False, recurssions:int = 0):
        import pdb
        #pdb.set_trace()
        """ Aux function. helps check_word"""
        LOG.debug("__recursive_parser: Begin ")
        if not isinstance(data, str):
            data = str(data)
        if recurssions > 16*len(data):
            LOG.debug("RECURSSION LIMIT")
            return TypeCheckList(ParseTree)
        if len(data) == 0:
            return TypeCheckList(ParseTree)
        #if(len(data) < 4):
        #    import pdb
        #    pdb.set_trace()
        from ..Symbol import TerminalSymbol, NullSymbol, NonTerminalSymbol
        if isinstance(onlysymbol, TerminalSymbol):
            #Locate every ocurrence of word and return a set of results. Follow boundariesrules
            LOG.debug("Iteration: terminalsymbol")
            sproduction = self._productionset.getProductionsBySide([onlysymbol])[0]
            result = terminal_symbol_consume(onlysymbol, data, sproduction )
            if showerrors and not result:
                LOG.debug("error symbolo: " + str(onlysymbol))
                #print("ERROR!: " + str(data) + str(onlysymbol))
                return TypeCheckList(ParseTree, [ParseTree(0,len(data), [onlysymbol] , data, sproduction, valid = False)])
            return result
        elif isinstance(onlysymbol, NonTerminalSymbol):
            result = TypeCheckList(ParseTree)
            tmpresults = []
            invalidlist = []
            for alternative in self._productionset.getProductionsBySide([onlysymbol]):
                alternativetree = RecursiveDescentResultTree(None)
                alternativesuccess = True
                alternativeinvalidlist = []
                for symbolindex, symbol in enumerate(alternative.rightside):
                    symbolsuccess = False
                    for totalpos in alternativetree.last_poss():
                        if totalpos >= len(data):
                            LOG.debug("Alternative length problem:" + str(alternative) + " Recursion: "+ str(recurssions) + " INTENTO SIMBOLO " + str(symbolindex) + ":" + str(symbol) +  " Input: "+ str(data) +" SHIFT " + str(totalpos))
                            continue
                        LOG.debug("Alternative:" + str(alternative) + " Recursion: "+ str(recurssions) + " INTENTO SIMBOLO " + str(symbolindex) + ":" + str(symbol) +  " Input: "+ str(data) +" SHIFT " + str(totalpos))
                        if symbol == onlysymbol:
                            #recurssions += 1
                            pass
                        thisresult =  self.__recursive_parser(symbol, data[totalpos:], alternative, showerrors, recurssions+1)
                        #pdb.set_trace()
                        #print("RECIBE: " + str([(str(x.leftpos),str(x.rightpos)) for x in thisresult]))
                        allvalids = all([x.valid for x in thisresult])
                        if thisresult and allvalids:
                            LOG.debug("Alternative:" + str(alternative) + " Recursion: "+ str(recurssions) + " Trying Symbol " + str(symbolindex) + ":" + str(symbol) +  " Input: "+ str(data) +" SHIFT " + str(totalpos)+  " results: " + str(thisresult) + "leftpos: " + str(thisresult[0].leftpos) + " rightpos: " + str(thisresult[-1].rightpos))
                            symbolsuccess = True
                            for x in thisresult:
                                x.shift(totalpos)
                                exito = alternativetree.append(x, totalpos)
                                if not exito:
                                    #TODO: Añadir como error al arbol o a otro sitio
                                    LOG.debug("Discarded symbol :" + str(symbol) + " position:" + str(totalpos))
                                else:
                                    LOG.debug("Added symbol :" + str(symbol) + " position:" + str(totalpos))
                        else:
                            for x in thisresult:
                                if not x.valid:
                                    alternativeinvalidlist.append(x)
                    if not symbolsuccess:
                        LOG.debug("Symbol doesn't work" + str(symbol))
                        alternativesuccess = False
                        break #Try another alternative
                    else:
                        LOG.debug("Symbol work at recursion" + str(recurssions) + ": " + str(symbol))
                if not alternativesuccess:
                    continue #A symbol doesn't work, this alternative doesn't neither
                else: 
                    invalidlist += alternativeinvalidlist

                for x in alternativetree.get_lists():
                    LOG.debug("Recurssion" + str(recurssions) + " Adding...",[y.content for y in x])
                    tmpresults.append(x)

            LOG.debug("La iteracion " + str(recurssions) + "result collection finished:" + str(tmpresults))
            for alternative in self._productionset.getProductionsBySide([onlysymbol]):
                for results in tmpresults:
                    allvalids = all([x.valid for x in results])
                    LOG.debug("result: " + str([x.content for x in results]) + ", alternative:" + str(alternative))
                    nullcounter = alternative.rightside.count(NullSymbol())
                    nnullresults = 0
                    for y in [x.symbollist for x in results]:
                        nnullresults += y.count(NullSymbol())
                    #print(len(results),nnullresults,len(alternative.rightside),nullcounter)
                    if len(results) - nnullresults != len(alternative.rightside) - nullcounter:
                        LOG.debug("Discarded: Bad result number")
                        continue
                    if results[-1].rightpos > len(data):
                        LOG.debug("Discarded: Bad rightpos")
                        continue
                    for x in range(min(len(alternative.rightside), len(results))):
                        #It is the same rule?
                        if results[x].content != alternative.rightside[x]:
                            continue
                    #print([(x.leftpos, x.rightpos) for x in results])
                    #print(recurssions, results[0].leftpos, results[-1].rightpos, allvalids, data, alternative)
                    newresult = ParseTree(0, results[-1].rightpos - results[0].leftpos, [onlysymbol], data[results[0].leftpos:results[-1].rightpos], production)
                    #print(newresult)
                    for child in results:
                        newresult.append_child(child)
                        if not child.valid:
                            newresult.valid = False
                    if newresult.valid:
                        result.append(newresult)
            if showerrors and not result:
                erroresult = TypeCheckList(ParseTree, [ParseTree(0,len(data), [onlysymbol] , data, production, valid = False)])
                for invalid in invalidlist:
                    if invalid.production.leftside[0] in production.rightside:
                        erroresult[0].append_child(invalid)
                return erroresult
            #LOG.debug("Returns: " + str([(str(x.leftpos),str(x.rightpos)) for x in result]))
            return result
        elif isinstance(onlysymbol, NullSymbol):
            return TypeCheckList(ParseTree,[ParseTree(0, 0, [onlysymbol], "", production)])
        else:
            raise Exception
