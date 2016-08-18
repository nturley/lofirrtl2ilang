import argparse
from antlr4 import *
from lofirrtlLexer import lofirrtlLexer
from listener import IlangListener
from lofirrtlParser import lofirrtlParser
from denting import Denter


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='lofirrtl input file path', required=True)
    parser.add_argument('-o','--output', help='ilang output file path')
    args = parser.parse_args()
    lexer = lofirrtlLexer(FileStream(args.input))
    lexer.denter = Denter(lexer)
    stream = CommonTokenStream(lexer)
    parser = lofirrtlParser(stream)
    tree = parser.circuit()

    ilang = IlangListener()
    walker = ParseTreeWalker()
    walker.walk(ilang, tree)
    if args.output:
        with open(args.output,'w+') as f:
            f.write(str(ilang))
    else:
        print ilang

if __name__ == '__main__':
    main()