"""
this module is for classes and methods that actually
parse and process the syntax tree
"""
from lofirrtlListener import lofirrtlListener
from ilang import Type, Wire, Cell, Module

class IlangListener(lofirrtlListener):
    """ this class follows a basic pattern
    * enterParent sets up default values and data structures in it's context
    * exitChild assigns values to the _parent_ context
    * exitParent packages module-level data and saves it in self
    Avoid accessing your children!
    """

    def __str__(self):
        ret = ''
        for mod in self.modules:
            ret += str(mod)
        return ret

    def enterCircuit(self, ctx):
        self.modules = []

    def enterModule(self, ctx):
        # reset self data, modules constitute a namespace
        self.wires = {}
        self.cells = []
        self.connects = []
        # for things that need unique names or numbers
        self.port_num = 1
        self.inferwire_num = 1
        self.cell_num = 1

    def enterModule_id(self, ctx):
        ctx.parentCtx.mod_id = '\\' + ctx.getText()

    def exitModule(self, ctx):
        mod = Module(ctx.mod_id,
                     self.wires,
                     self.cells,
                     self.connects)
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

    def exitWidth(self, ctx):
        ctx.parentCtx.ftype.width = ctx.ival

    def exitFtype(self, ctx):
        ctx.parentCtx.wire.ftype = ctx.ftype

    def exitPort(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire

    def enterReg(self, ctx):
        # register is a special type of wire
        ctx.wire = Wire()
        ctx.wire.is_reg = True

    def enterReg_id(self, ctx):
        ctx.parentCtx.wire.wire_id = '\\'+ ctx.getText()

    def exitReg(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire

    def enterNode(self, ctx):
        # honestly, I don't see why nodes even exist
        # they are exactly like wires!
        ctx.wire = Wire()

    def enterNode_id(self, ctx):
        ctx.parentCtx.wire.wire_id = '\\'+ ctx.getText()

    def exitNode_val(self, ctx):
        ctx.parentCtx.wire.ftype = ctx.ftype
        if hasattr(ctx, 'ret_cell'):
            ctx.parentCtx.cell = ctx.ret_cell
        if hasattr(ctx, 'val'):
            ctx.parentCtx.val = ctx.val

    def exitNode(self, ctx):
        self.wires[ctx.wire.wire_id] = ctx.wire
        if hasattr(ctx, 'cell'):
            ctx.cell.ret_val = ctx.wire.wire_id
        else:
            # you must be a reference or constant
            self.connects.append((ctx.wire.wire_id, ctx.val))

    def enterExp(self, ctx):
        ctx.is_op = False

    def exitExp(self, ctx):
        if hasattr(ctx, 'ftype'):
            ctx.parentCtx.ftype = ctx.ftype
            ctx.parentCtx.is_op = ctx.is_op
        if hasattr(ctx, 'val'):
            ctx.parentCtx.val = ctx.val
        if hasattr(ctx, 'ret_cell'):
            ctx.parentCtx.ret_cell = ctx.ret_cell

    def enterRef(self, ctx):
        refname = '\\' + ctx.getText()
        # does this reference something we know?
        if refname in self.wires:
            wire = self.wires[refname]
            ctx.parentCtx.ftype = wire.ftype
            ctx.parentCtx.val = refname

    def enterConst(self, ctx):
        ctx.ftype = Type()
        if ctx.getText()[0] is 'S':
            ctx.ftype.signed = True

    def exitConst_ival(self, ctx):
        ctx.parentCtx.val = ctx.ival

    def enterConst_bval(self, ctx):
        ctx.parentCtx.val = ctx.getText()

    def exitConst(self, ctx):
        ctx.parentCtx.ftype = ctx.ftype
        ctx.parentCtx.val = ctx.val

    def enterPrimop(self, ctx):
        ctx.argtypes = []
        ctx.argvals = []
        ctx.params = []
        ctx.opname = None

    def exitConnected_lhs(self, ctx):
        ctx.parentCtx.lhs = ctx.val

    def exitConnected_rhs(self, ctx):
        if hasattr(ctx, 'ret_cell'):
            ctx.parentCtx.cell = ctx.ret_cell
        if hasattr(ctx, 'val'):
            ctx.parentCtx.val = ctx.val

    def exitConnect(self, ctx):
        if hasattr(ctx, 'cell'):
            ctx.cell.ret_val = ctx.lhs
        else:
            self.connects.append((ctx.lhs, ctx.val))

    def enterPrimop_name(self, ctx):
        ctx.parentCtx.opname = ctx.getText()[:-1]

    def exitOp_argument(self, ctx):
        ctx.parentCtx.argtypes.append(ctx.ftype)
        # prim_op
        if hasattr(ctx, 'is_op') and ctx.is_op:
            inferwire = Wire()
            inferwire.ftype = ctx.ftype
            inferwire.wire_id = '\\INFER_' + str(self.inferwire_num)
            self.inferwire_num += 1
            self.wires[inferwire.wire_id] = inferwire
            ctx.parentCtx.argvals.append(inferwire.wire_id)
            ctx.ret_cell.ret_val = inferwire.wire_id
        # constant
        if hasattr(ctx, 'val'):
            ctx.parentCtx.argvals.append(ctx.val)

    def exitOp_parameter(self, ctx):
        ctx.parentCtx.params.append(int(ctx.getText()))

    def exitPrimop(self, ctx):
        ftype = primop_type(ctx.opname, ctx.argtypes, ctx.params)
        ctx.parentCtx.ftype = ftype
        ctx.parentCtx.is_op = True
        cell = Cell(op_name=ctx.opname,
                    ret_type=ftype,
                    arg_vals=ctx.argvals,
                    arg_types=ctx.argtypes,
                    unique_name='\\CELL_'+str(self.cell_num))
        self.cell_num += 1
        self.cells.append(cell)
        ctx.parentCtx.ret_cell = cell

    def enterIntLit(self, ctx):
        ctx.parentCtx.ival = parse_int(ctx.getText())


def parse_int(s):
    """ This is not compliant to spec
    but FIRRTL isn't either yet """
    if s == '0':
        return 0
    if s.startswith('"h'):
        return int(s[2:-1],16)
    return int(s)


def primop_type(op, arg, param):
    """ There's a terrible table in the spec that lays all of this
    data out. It's terrible. I couldn't see any other way to code this"""
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