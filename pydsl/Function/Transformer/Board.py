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

"""Boards"""

__author__ = "Nestor Arocha Rodriguez"
__copyright__ = "Copyright 2008-2012, Nestor Arocha Rodriguez"
__email__ = "nesaro@gmail.com"

import logging
from pydsl.Function.Function import Function
from .Network import HostFunctionNetwork
from pydsl.Function.Transformer.Transformer import Transformer
LOG = logging.getLogger(__name__)

class Board(Transformer, HostFunctionNetwork):
    """A Transformer where you can call other Transformer. Doesn't perform any computation"""

    from pydsl.Abstract import Event

    def __init__(self, gtenvdefinitionslist:list, ecuid = None, server = None, timeout = 10):
        if ecuid != None:
            from .Network import FunctionNetworkServer
            if not isinstance(server, FunctionNetworkServer):
                raise TypeError("FunctionNetworkServer expected, got %s" % str(server))
        self.__timeout = timeout
        self.__GTDefinitionlist = gtenvdefinitionslist #list to put every gt envdefinition
        self.__inputGTDict = {} #{"channelname":GTinstance,} #Inner GT that receives input
        self.__outputGTDict = {} #{"channelname":GTinstance,}
        HostFunctionNetwork.__init__(self)
        inputgrammars, outputgrammars = self.__extractExternalChannelGrammarsFromDefinitions()
        Transformer.__init__(self, inputgrammars, outputgrammars, ecuid, server)
        import threading
        self.__event = threading.Event()
        self.__loadTfromDefinitionList()
        self.__worklock = threading.Lock()
        self.__connectAllGTs()
        self.__run()

    @property
    def summary(self):
        from pydsl.Abstract import InmutableDict
        inputdic = [ x.identifier for x in self.inputchanneldic.values() ]
        outputdic = [ x.identifier for x in self.outputchanneldic.values() ]
        result = {"iclass":"Board", "input":inputdic, "output":outputdic, "ancestors":self.ancestors()}
        return InmutableDict(result)

    def __call__(self, inputdict:dict):
        LOG.debug(" received dic:" + str(inputdict))
        if not inputdict:
            LOG.error("No input")
            return None
        with self.__worklock:
            import random
            rand = random.randint(1, 999999)
            self.__event.clear()
            for channel, strcontent in inputdict.items():
                LOG.debug("Board Receiving: " + channel + " " + str(strcontent))
                self.__sendToChannel(channel, rand, strcontent)
            # ctime = now()
            while True:
                self.__event.wait(self.__timeout)
                if not self.__event.isSet():
                    LOG.error("Board: TIMEOUT")
                    #emit error to parent
                    #delete rand in msgqueue
                    from pydsl.Function.Function import Error
                    newerror = Error("Timeout")
                    newerror.appendSource(self.ecuid.name)
                    return newerror
                # if there is an error assoc to rand:
                    # emit error to parent
                    # delete rand in msgqueue
                    # return {}
                error = self._queue.getErrorById(rand)
                if error != None:
                    error.appendSource(self.ecuid.name)
                    return error
                uidlist = []
                for x in self.__outputGTDict.values():
                    uidlist.append(self._hostT[x[0]].ecuid)
                resultdic = self._queue.getResultsByMask(uidlist, rand)
                if not resultdic:
                    self.__event.clear()
                    continue
                else:
                    break
                #result = self.__outputIOObject.getLog()[rand]
                #self.__outputIOObject.delLog(rand)
            #returns dict {outputchannelname:word,}
            uidlist = []
            translationdic = {}

            #Extract all child identifiers

            for key, value in self.__outputGTDict.items():
                uidlist.append(self._hostT[value[0]].ecuid)
                translationdic[value[0]] = (value[1], key)
            resultdic2 = {}
            #copia los valores
            #Translates output names
            for uid in uidlist:
                assert(len(resultdic[uid]) == 1)
                resultdic2[translationdic[uid.name][1]] = resultdic[uid][translationdic[uid.name][0]]
            return resultdic2

    def __extractExternalChannelGrammarsFromDefinitions(self):
        """Extracts grammars from definition.
        generated channel must be connected to outside elements"""
        inputtypedict = {}
        outputtypedict = {}
        for definition in self.__GTDefinitionlist:
            for gtcondef in definition.inputConnectionDefinitions:
                if gtcondef.externalgtname == "Main":
                    if gtcondef.internalchannelname in inputtypedict:
                        from pydsl.Exceptions import NameOverlap
                        raise NameOverlap
                    #FIXME: Is better to avoid loading the instance to obtain grammar name
                    from pydsl.Memory.Storage.Loader import load_transformer
                    gtinstance = load_transformer(definition.type)
                    inputtypedict[gtcondef.externalchannelname] = gtinstance.inputdefinition[gtcondef.internalchannelname]
                    self.__inputGTDict[gtcondef.externalchannelname] = (gtcondef.basename, gtcondef.internalchannelname) #Prepares self.__inputGTDict
            for gtcondef in definition.outputConnectionDefinitions:
                if gtcondef.externalgtname == "Main":
                    if gtcondef.internalchannelname in outputtypedict:
                        from pydsl.Exceptions import NameOverlap
                        raise NameOverlap
                    from pydsl.Memory.Storage.Loader import load_transformer
                    gtinstance = load_transformer(definition.type)
                    ocd = gtinstance.outputchanneldic
                    outputtypedict[gtcondef.externalchannelname] = gtinstance.outputdefinition[gtcondef.internalchannelname]
                    self.__outputGTDict[gtcondef.externalchannelname] = (gtcondef.basename, gtcondef.internalchannelname) #Prepares self.__outputGTDict
        return (inputtypedict, outputtypedict)

    def __loadTfromDefinitionList(self):
        """GTDefinitions -> Instances"""
        from pydsl.Memory.Storage.Directory.BoardSection import BoardDefinitionSection
        auxnametype = {}
        for definition in self.__GTDefinitionlist:
            if not isinstance(definition, BoardDefinitionSection):
                raise TypeError
            gtname = definition.name
            gttype = definition.type
            auxnametype[gtname] = gttype
        self._initHostT(auxnametype)
        LOG.debug("__loadTfromDefinitionList: loaded __GTs: " + str(self._hostT.keys()))

    def __connectAllGTs(self):
        """Connect all instances"""
        from pydsl.Memory.Storage.Directory.BoardSection import BoardConnectionDefinition
        for definition in self.__GTDefinitionlist:
            gtname = definition.name
            outputgrammarlist = definition.outputConnectionDefinitions
            gtinstance = self._hostT[gtname]
            for gtcondef in outputgrammarlist:
                if not isinstance(gtcondef, BoardConnectionDefinition):
                    raise TypeError
                if gtcondef.externalgtname != "Main":
                    gtinstance.connect(gtcondef.internalchannelname, self._hostT[gtcondef.externalgtname], gtcondef.externalchannelname)

    def __sendToChannel(self, inputchannel, msgid, data):
        """Sends communication to an internal Transformer"""
        internalt, internalchannel = self.__inputGTDict[inputchannel]
        self._hostT[internalt].receive(internalchannel, msgid, data)

    def __run(self):
        self._server.start()

    from .Network import FunctionNetworkClient
    def registerInstance(self, name, client:FunctionNetworkClient):
        self._server.registerInstance(name, client)

    def _onReceiveEvent(self, event:Event):
        """Receive message as a client"""
        LOG.debug(str(self.identifier) + ":__receiveMSGFunction: Begin")
        from pydsl.Function.Function import Error
        if isinstance(event.msg, Error):
            #Grammar error, abort
            self.__event.set()
        elif event.msg:
            self.__event.set() #TODO: Check event source
            #Event sent by this element to finish waiting 
        else:
            from pydsl.Exceptions import EventError
            raise EventError

    def __receiveEventAsServer(self, event:Event):
        """Receives message as server"""
        #LOG.debug(str(self.identifier) + ":__receiveEventAsServer: Begin")
        from pydsl.Function.Function import Error
        if event.msg:
            if event.source != self.ecuid and event.source != self._server.ecuid:
                self._queue.append(event)
            self.__event.set() 
        elif isinstance(event.msg, Error):
            #Grammar error, abort
            self._queue.append(event)
            self.__event.set()
        else:
            from pydsl.Exceptions import EventError
            LOG.error("Unknown event type")
            raise EventError

    def handleEvent(self, event:Event):
        """Handle message As a server"""
        if event.destination in self.ecuid or event.source == self.ecuid:
            self.__receiveEventAsServer(event)
        else:
            HostFunctionNetwork.handleEvent(self, event)

    def __str__(self):
        result = "<B " + str(self.identifier) + " "
        result += "input: " + str(self.inputchanneldic)
        result += "output: " + str(self.outputchanneldic)
        result += "inputGT: " + str(self.__inputGTDict)
        result += "outputGT: " + str(self.__outputGTDict)
        result += "connections: " + str(self._connections)
        result += ">"
        return result