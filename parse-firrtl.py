from antlr4 import *
from FIRRTLLexer import FIRRTLLexer
from FIRRTLListener import FIRRTLListener
from FIRRTLParser import FIRRTLParser
from denting import Denter
import sys


class Wire:
    def __init__(self):
        self.wire_id = None
        self.width = 1
        self.signed = False
        self.port_dir = None
        self.port_num = None

    def __str__(self):
        ret = 'wire'
        if self.port_dir:
            ret += ' ' + self.port_dir + ' ' + str(self.port_num)
        if self.width > 1:
            ret += ' width ' + str(self.width)
        ret += ' ' + self.wire_id
        return ret

class Module:
    def __init__(self, fid):
        self.fid = fid

class FIRRTLPrintListener(FIRRTLListener):
    def setupMembers(self):
        self.wires = {}
        self.currWire = None
        self.port_num = 1

    def enterModule_id(self, ctx):
        print 'module \\' + ctx.getText()

    def exitModule(self, ctx):
        print 'end'

    def enterPort(self, ctx):
        self.currWire = Wire()
        self.currWire.port_num = self.port_num

    def enterPort_id(self, ctx):
        self.currWire.wire_id = '\\'+ ctx.getText()

    def enterPort_dir(self, ctx):
        self.currWire.port_dir = ctx.getText()

    def exitPort(self, ctx):
        self.wires[self.currWire.wire_id] = self.currWire
        print '  ' + str(self.currWire)
        self.currWire = None
        self.port_num += 1

    def enterReg(self, ctx):
        self.currWire = Wire()

    def enterReg_id(self, ctx):
        self.currWire.wire_id = ctx.getText()

    def exitReg(self, ctx):
        print '  ' + str(self.currWire)
        self.currWire = None

    def enterPort_type(self, ctx):
        if ctx.getText()[0] is 'S':
            self.currWire.signed = True

    def enterFtype_width(self, ctx):
        if self.currWire:
            self.currWire.width = int(ctx.getText())


def main():
    lexer = FIRRTLLexer(FileStream('example.fir'))
    lexer.denter = Denter(lexer)
    stream = CommonTokenStream(lexer)
    parser = FIRRTLParser(stream)
    tree = parser.circuit()

    printer = FIRRTLPrintListener()
    printer.setupMembers()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main()