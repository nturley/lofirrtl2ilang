from antlr4 import *
from lofirrtlLexer import lofirrtlLexer
from lofirrtlListener import lofirrtlListener
from lofirrtlParser import lofirrtlParser
from denting import Denter
import sys

def primop_type(op, arg, param):
    t = Type()
    if op == 'add':
        t.signed = arg[0].signed or arg[1].signed
        t.width = max(arg[0].width, arg[1].width) + 1
    elif op == 'sub':
        t.signed = True
        t.width = max(arg[0].width, arg[1].width) + 1
    elif op == 'mul':
        t.signed = arg[0].signed or arg[1].signed
        t.width = arg[0].width + arg[1].width
    elif op == 'div':
        t.signed = arg[0].signed or arg[1].signed
        t.width = arg[0].width
        if arg[1].signed: t.width += 1
    elif op == 'mod':
        t.signed = arg[0].signed
        t.width = min(arg[0].width, arg[1].width)
        if arg[0].signed and not arg[1].signed: t.width + 1
    elif op in ['lt','leq','gt','geq','eq','neq']:
        t.signed = False
        t.width = 1
    elif op == 'pad':
        t.signed = arg[0].signed
        t.width = max(arg[0].width, param[0])
    elif op == 'asUInt':
        t.signed = False
        t.width = arg[0].width
    elif op == 'asSInt':
        t.signed = True
        t.width = arg[0].width
    elif op == 'asClock':
        t.signed = False
        t.width = 1
    elif op == 'shl':
        t.signed = arg[0].signed
        t.width = arg[0].width + param[0]
    elif op == 'shl':
        t.signed = arg[0].signed
        t.width = arg[0].width - param[0]
    elif op == 'dshl':
        t.signed = arg[0].signed
        t.width = arg[0].width + 2**(arg[1].width)
    elif op == 'dshr':
        t.signed = arg[0].signed
        t.width = arg[0].width
    elif op == 'cvt':
        t.signed = True
        t.width = arg[0].width
        if not arg[0].signed: t.width += 1
    elif op == 'neg':
        t.signed = True
        t.width = arg[0].width + 1
    elif op == 'not':
        t.signed = False
        t.width = arg[0].width
    elif op in ['and', 'or', 'not']:
        t.signed = False
        t.width = max(arg[0].width, arg[1].width)
    elif op in ['andr', 'orr', 'xorr']:
        t.signed = False
        t.width = 1
    elif op == 'cat':
        t.signed = False
        t.width = arg[0].width + arg[1].width
    elif op == 'bits':
        t.signed = arg[0].signed
        t.width = param[0]-param[1]+1
    elif op == 'head':
        t.signed = False
        t.width = param[0]
    elif op == 'tail':
        t.signed = False
        t.width = arg[0].width - param[0]
    return t

class Type:
    def __init__(self, signed=False, width=1):
        self.signed = signed
        self.width = width
    def __str__(self):
        ret = 'UInt'
        if self.signed:
            ret = 'SInt'
        ret += '<'+str(self.width)+'>'
        return ret

class Wire:
    def __init__(self):
        self.wire_id = None
        self.ftype = Type()
        self.port_dir = None
        self.port_num = None
        self.unknown_type = False

    def __str__(self):
        ret = 'wire'
        if self.port_dir:
            ret += ' ' + self.port_dir + ' ' + str(self.port_num)
        if self.ftype.width > 1:
            ret += ' width ' + str(self.ftype.width)
        ret += ' ' + self.wire_id
        return ret

class Module:
    def __init__(self, fid):
        self.fid = fid

class lofirrtlPrintListener(lofirrtlListener):
    def setupMembers(self):
        self.wires = {}
        self.currWire = None
        self.port_num = 1
        self.anonwire_num = 1

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
        self.currWire.wire_id = '\\' + ctx.getText()

    def exitReg(self, ctx):
        self.wires[self.currWire.wire_id] = self.currWire
        print '  ' + str(self.currWire)
        self.currWire = None

    def enterPort_type(self, ctx):
        if ctx.getText()[0] is 'S':
            self.currWire.ftype.signed = True

    def enterFtype_width(self, ctx):
        if self.currWire:
            self.currWire.ftype.width = int(ctx.getText())

    def enterNode(self, ctx):
        self.currWire = Wire()
        self.unknown_type = True

    def exitNode(self, ctx):
        self.wires[self.currWire.wire_id] = self.currWire
        if hasattr(ctx.exp(),'ftype'):
            self.currWire.ftype = ctx.exp().ftype
            print '  ' + str(self.currWire)
        self.currWire = None

    def enterNode_id(self, ctx):
        self.currWire.wire_id = '\\' + ctx.getText()

    def exitExp(self, ctx):
        # if you know your type, tell your parent
        if hasattr(ctx, 'ftype'):
            ctx.parentCtx.ftype = ctx.ftype

    def enterRef(self, ctx):
        refname = '\\' + ctx.getText()
        # does this reference something we know?
        if refname in self.wires:
            wire = self.wires[refname]
            # tell exp your type
            ctx.parentCtx.ftype = wire.ftype
        else:
            if self.currWire.wire_id != refname:
                print 'cant find: ' + refname

    def exitConst(self, ctx):
        # tell exp your type
        const_type = Type()
        if ctx.getText()[0] is 'S':
            const_type.signed = True
        const_type.width = int(ctx.const_width().getText())
        ctx.parentCtx.ftype = const_type

    def exitMux_pred_high(self, ctx):
        # if you know your type, tell mux
        if hasattr(ctx,'ftype'):
            ctx.parentCtx.high_type = ctx.ftype

    def exitMux_pred_else(self, ctx):
        # if you know your type, tell mux
        if hasattr(ctx,'ftype'):
            ctx.parentCtx.else_type = ctx.ftype

    def exitMux(self, ctx):
        # if either of your kids know their type, tell your parent
        if hasattr(ctx,'high_type'):
            ctx.parentCtx.ftype = ctx.high_type
        elif hasattr(ctx,'else_type'):
            ctx.parentCtx.ftype = ctx.else_type
        else:
            print 'something screwy is going on here'

    def enterValid_in(self, ctx):
        # if you know your type, tell your parent
        if hasattr(ctx,'ftype'):
            ctx.parentCtx.ftype = ctx.ftype

    def exitValidif(self, ctx):
        # if you know your type, tell your parent
        if hasattr(ctx,'ftype'):
            ctx.parentCtx.ftype = ctx.ftype

    def enterPrimop(self, ctx):
        ctx.argtypes = []
        ctx.params = []
        ctx.opname = None

    def enterPrimop_name(self, ctx):
        ctx.parentCtx.opname = ctx.getText()[:-1]

    def exitPrimop_name(self, ctx):
        ctx.parentCtx.opname = ctx.getText()[:-1]

    def exitOp_argument(self, ctx):
        if hasattr(ctx,'ftype'):
            ctx.parentCtx.argtypes.append(ctx.ftype)

    def exitOp_parameter(self, ctx):
        ctx.parentCtx.params.append(int(ctx.getText()))

    def exitPrimop(self, ctx):
        ftype = primop_type(ctx.opname, ctx.argtypes, ctx.params)
        ctx.parentCtx.ftype = ftype

def main():
    lexer = lofirrtlLexer(FileStream('lofirrtl/gcd.fir'))
    lexer.denter = Denter(lexer)
    stream = CommonTokenStream(lexer)
    parser = lofirrtlParser(stream)
    tree = parser.circuit()

    printer = lofirrtlPrintListener()
    printer.setupMembers()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main()