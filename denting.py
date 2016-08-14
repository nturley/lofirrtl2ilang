from FIRRTLParser import FIRRTLParser
from antlr4 import Token, Lexer
from antlr4.Token import CommonToken

NEWLINE = FIRRTLParser.NEWLINE
INDENT = FIRRTLParser.INDENT
DEDENT = FIRRTLParser.DEDENT

class Denter:
    def __init__(self, lexer):
        self.lexer = lexer
        self.dents_buffer = []
        self.indentations = []
        self.reached_eof = False

    def apply_eof(self, t):
        if len(self.indentations) is 0:
            r = self.createToken(NEWLINE, t)
        else:
            r = self.unwindto(0, t)
        self.dents_buffer.append(t)
        self.reached_eof = True
        return r

    def next_token(self):
        self.init_if_first()
        if len(self.dents_buffer) is 0:
            t = self.pull_token()
        else:
            t = self.dents_buffer.pop(0)
        if self.reached_eof:
            return t
        if t.type is NEWLINE:
            r = self.handle_newline(t)
        elif t.type is Token.EOF:
            r = self.apply_eof(t)
        else:
            r = t
        return r

    def pull_token(self):
        return Lexer.nextToken(self.lexer)

    def init_if_first(self):
        # first invocation
        if len(self.indentations) is 0:
            self.indentations.append(0)

            # find first non-new line
            while True:
                first_real_token = self.pull_token()
                if first_real_token.type is not NEWLINE:
                    break

            if first_real_token.column > 0:
                self.indentations.append(first_real_token.column)
                self.dents_buffer.append(createToken(INDENT, first_real_token))
            self.dents_buffer.append(first_real_token)

    def handle_newline(self, t):
        nextnext = self.pull_token()
        while nextnext.type is NEWLINE:
            t = nextnext
            nextnext = self.pull_token()
        if nextnext.type is Token.EOF:
            return self.apply_eof(nextnext)

        nltext = t.text
        indent = len(nltext) - 1
        if indent > 0 and nltext[0] is '/r':
            indent -= 1
        previndent = self.indentations[-1]
        if indent is previndent:
            r = t # just a newline
        elif indent > previndent:
            r = self.createToken(INDENT, t)
            self.indentations.append(indent)
        else:
            r = self.unwindto(indent, t)
        self.dents_buffer.append(nextnext)

        return r

    def createToken(self, toktype, copyfrom):
        toktype_to_typestr = {NEWLINE: '<NEWLINE>',
                          INDENT:  '<INDENT>',
                          DEDENT:  '<DEDENT>'}
        typestr = toktype_to_typestr[toktype]
        r = copyfrom.clone()
        r.type = toktype
        return r

    def unwindto(self, targetindent, copyfrom):
        assert len(self.dents_buffer) is 0
        self.dents_buffer.append(self.createToken(NEWLINE, copyfrom))
        # To make things easier, we'll queue up ALL of the dedents, and then pop off the first one.
        # For example, here's how some text is analyzed:
        #
        #  Text          :  Indentation  :  Action         : Indents Deque
        #  [ baseline ]  :  0            :  nothing        : [0]
        #  [   foo    ]  :  2            :  INDENT         : [0, 2]
        #  [    bar   ]  :  3            :  INDENT         : [0, 2, 3]
        #  [ baz      ]  :  0            :  DEDENT x2      : [0]
        while True:
            previndent = self.indentations.pop()
            if previndent is targetindent:
                break
            if targetindent > previndent:
                self.indentations.append(previndent)
                self.dents_buffer.append(self.createToken(INDENT, copyfrom))
                break
            self.dents_buffer.append(self.createToken(DEDENT, copyfrom))
        self.indentations.append(targetindent)
        return self.dents_buffer.pop(0)









