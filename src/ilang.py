"""
This module is for data structures that store ilang data
"""

class Type:
    """Type just holds the signedness and width of a signal/port"""
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
    """represents a signal, port, or register"""
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

class Cell:
    """represents an operator. We are going to assume
    that all lofirrtl operators can map to some cell"""
    def __init__(self,
                 op_name,
                 ret_type,
                 arg_vals,
                 arg_types,
                 unique_name):
        self.op_name = op_name
        self.ret_type = ret_type
        self.arg_vals = arg_vals
        self.arg_types= arg_types
        self.ret_val = None
        self.unique_name = unique_name

    def __str__(self):
        ret = '  cell $' + self.op_name + ' '
        ret += self.unique_name + '\n'
        if len(self.arg_types)>2:
            self.arg_types = self.arg_types[1:] + [self.arg_types[0]]
            self.arg_vals = self.arg_vals[1:] + [self.arg_vals[0]]
        arg_names = ['A','B','S']
        for i, arg_type in enumerate(self.arg_types):
            ret += '    parameter \\'
            ret += arg_names[i]
            ret += '_SIGNED '
            if arg_type.signed:
                ret += '1'
            else:
                ret += '0'
            ret += '\n    parameter \\'
            ret += arg_names[i]
            ret += '_WIDTH '
            ret += str(arg_type.width) + '\n'
        ret += '    parameter \\Y_WIDTH '
        ret += str(self.ret_type.width) + '\n'
        for i, arg in enumerate(self.arg_vals):
            ret += '    connect \\'
            ret += arg_names[i]
            ret += ' ' + str(arg) + '\n'
        ret += '    connect \\Y '
        ret += str(self.ret_val)
        ret += '\n  end\n'
        return ret

class Module:
    """ ilang modules are a collection of wires, cells, and connects"""
    def __init__(self, mod_id, wires, cells, connects):
        self.mod_id = mod_id
        self.wires = wires
        self.cells = cells
        self.connects = connects

    def __str__(self):
        ret = 'module ' + self.mod_id + '\n'
        for wire in self.wires.values():
            ret += '  ' + str(wire) + '\n'
        for cell in self.cells:
            ret += str(cell)
        for connect in self.connects:
            ret += '  connect '
            ret += connect[0] + ' ' + connect[1] + '\n'
        ret += 'end\n'
        return ret