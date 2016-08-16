from antlr4 import *
from lofirrtlLexer import lofirrtlLexer
from lofirrtlListener import lofirrtlListener
from lofirrtlParser import lofirrtlParser
from denting import Denter
import sys


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
        self.ftype = None
        self.port_dir = None
        self.port_num = None
        self.is_reg = False

    def __str__(self):
        ret = 'wire'
        if self.port_dir:
            ret += ' ' + self.port_dir + ' ' + str(self.port_num)
        if self.ftype.width > 1:
            ret += ' width ' + str(self.ftype.width)
        ret += ' ' + self.wire_id
        return ret

easy_cells = {'add'  : 'add',
              'sub'  : 'sub',
              'mul'  : 'mul',
              'div'  : 'div',
              'rem'  : 'mod',
              'lt'   : 'lt',
              'leq'  : 'le',
              'gt'   : 'gt',
              'geq'  : 'ge',
              'eq'   : 'eq',
              'shl'  : 'shl'
              'shr'  : 'shr'
              'neg'  : 'neg'
              'not'  : 'not'
              'and'  : 'and'
              'or'   : 'or'
              'xor'  : 'xor'
              'andr' : 'reduce_and'
              'orr'  : 'reduce_or'
              'xorr' : 'reduce_xor'
              'mux'  : 'mux'}

class Cell:
    def __init__(self):
        self.params = []
        self.connects = []

class Module:
    def __init__(self, mod_id, wires):
        self.mod_id = mod_id
        self.wires = wires

    def __str__(self):
        ret = 'module ' + self.mod_id + '\n'
        for wire in self.wires.values():
            ret += '  ' + str(wire) + '\n'
        ret += 'end\n'
        return ret

class lofirrtlPrintListener(lofirrtlListener):

    def __str__(self):
        ret = ''
        for mod in self.modules:
            ret += str(mod)
        return ret

    def enterCircuit(self, ctx):
        self.modules = []

    def enterModule(self, ctx):
        # global data in module
        self.wires = {}
        self.cells = []
        self.port_num = 1
        self.inferwire_num = 1

    def enterModule_id(self, ctx):
        ctx.parentCtx.mod_id = '\\' + ctx.getText()

    def exitModule(self, ctx):
        mod = Module(ctx.mod_id, self.wires)
        self.modules.append(mod)

    def enterPort(self, ctx):
        ctx.wire = Wire()
        ctx.wire.port_num = self.port_num
        self.port_num += 1

    def enterPort_id(self, ctx):
        ctx.parentCtx.wire.wire_id = '\\'+ ctx.getText()

    def enterPort_dir(self, ctx):
        ctx.parentCtx.wire.port_dir = ctx.getText()

    def enterFtype(self, ctx):
        ctx.ftype = Type()
        if ctx.getText()[0] is 'S':
            ctx.ftype.signed = True

    def enterWidth(self, ctx):
        ctx.parentCtx.ftype.width = int(ctx.getText())

    def exitFtype(self, ctx):
        ctx.parentCtx.wire.ftype = ctx.ftype

    def exitPort(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire

    def enterReg(self, ctx):
        ctx.wire = Wire()
        ctx.wire.is_reg = True

    def enterReg_id(self, ctx):
        ctx.parentCtx.wire.wire_id = '\\'+ ctx.getText()

    def exitReg(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire

    def enterNode(self, ctx):
        ctx.wire = Wire()

    def enterNode_id(self, ctx):
        ctx.parentCtx.wire.wire_id = '\\'+ ctx.getText()

    def exitNode_val(self, ctx):
        ctx.parentCtx.wire.ftype = ctx.ftype

    def exitNode(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire

    def enterExp(self, ctx):
        ctx.is_op = False

    def exitExp(self, ctx):
        if hasattr(ctx, 'ftype'):
            ctx.parentCtx.ftype = ctx.ftype
            ctx.parentCtx.is_op = ctx.is_op

    def enterRef(self, ctx):
        refname = '\\' + ctx.getText()
        # does this reference something we know?
        if refname in self.wires:
            wire = self.wires[refname]
            ctx.parentCtx.ftype = wire.ftype

    def enterConst(self, ctx):
        ctx.ftype = Type()
        if ctx.getText()[0] is 'S':
            ctx.ftype.signed = True

    def enterConst_ival(self, ctx):
        ctx.parentCtx.val = ctx.getText()
        ctx.parentCtx.valtype = 'i'

    def enterConst_bval(self, ctx):
        ctx.parentCtx.val = ctx.getText()
        ctx.parentCtx.valtype = 'b'-0

    def exitConst(self, ctx):
        ctx.parentCtx.ftype = ctx.ftype
        ctx.parentCtx.val = ctx.val
        ctx.parentCtx.valtype = ctx.valtype

    def enterPrimop(self, ctx):
        ctx.argtypes = []
        ctx.params = []
        ctx.opname = None

    def enterPrimop_name(self, ctx):
        ctx.parentCtx.opname = ctx.getText()[:-1]

    def exitOp_argument(self, ctx):
        ctx.parentCtx.argtypes.append(ctx.ftype)
        if hasattr(ctx, 'is_op') and ctx.is_op:
            inferwire = Wire()
            inferwire.ftype = ctx.ftype
            inferwire.wire_id = '\\INFER_' + str(self.inferwire_num)
            self.inferwire_num += 1
            self.wires[inferwire.wire_id] = inferwire

    def exitOp_parameter(self, ctx):
        ctx.parentCtx.params.append(int(ctx.getText()))

    def exitPrimop(self, ctx):
        ftype = primop_type(ctx.opname, ctx.argtypes, ctx.params)
        ctx.parentCtx.ftype = ftype
        ctx.parentCtx.is_op = True
        if ctx.opname in easy_cells:
            cell = Cell()


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
    elif op == 'rem':
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
    elif op in ['mux', 'validif']:
        t.signed = arg[1].signed
        t.width = arg[1].width
    return t


def main():
    lexer = lofirrtlLexer(FileStream('lofirrtl/gcd.fir'))
    lexer.denter = Denter(lexer)
    stream = CommonTokenStream(lexer)
    parser = lofirrtlParser(stream)
    tree = parser.circuit()

    printer = lofirrtlPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    print printer

if __name__ == '__main__':
    main()