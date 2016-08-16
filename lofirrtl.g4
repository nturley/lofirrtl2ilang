/*
Copyright (c) 2014 - 2016 The Regents of the University of
California (Regents). All Rights Reserved.  Redistribution and use in
source and binary forms, with or without modification, are permitted
provided that the following conditions are met:
   * Redistributions of source code must retain the above
     copyright notice, this list of conditions and the following
     two paragraphs of disclaimer.
   * Redistributions in binary form must reproduce the above
     copyright notice, this list of conditions and the following
     two paragraphs of disclaimer in the documentation and/or other materials
     provided with the distribution.
   * Neither the name of the Regents nor the names of its contributors
     may be used to endorse or promote products derived from this
     software without specific prior written permission.
IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS,
ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF
REGENTS HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF
ANY, PROVIDED HEREUNDER IS PROVIDED "AS IS". REGENTS HAS NO OBLIGATION
TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
MODIFICATIONS.
*/



grammar lofirrtl;

tokens { INDENT, DEDENT }

@lexer::members {
# START SPECIAL MEMBER
def nextToken(self):
    return self.denter.next_token()
# END SPECIAL MEMBER
}

/*------------------------------------------------------------------
 * PARSER RULES
 *------------------------------------------------------------------*/

/* TODO
 *  - Add [info] support (all over the place)
 *  - Add support for extmodule
*/

// Does there have to be at least one module?
circuit
  : 'circuit' fid ':' info? INDENT module* DEDENT
  ;

module
  : 'module' module_id ':' info? INDENT port* moduleBlock DEDENT
  | 'extmodule' fid ':' info? INDENT port* DEDENT
  ;

module_id
  : fid
  ;

port
  : port_dir port_id ':' ftype info? NEWLINE
  ;

port_id
  : fid
  ;

port_dir
  : 'input'
  | 'output'
  ;

ftype
  : 'UInt' '<' width '>'
  | 'SInt' '<' width '>'
  | 'Clock'
  ;

width
  : IntLit
  ;

moduleBlock
  : simple_stmt*
  ;

simple_reset0
  :  'reset' '=>' '(' reset_signal init_val ')'
  ;

reset_signal
  : exp
  ;

init_val
  : exp
  ;

simple_reset
	: simple_reset0
	| '(' simple_reset0 ')'
	;

reset_block
	: INDENT simple_reset NEWLINE DEDENT
	| '(' +  simple_reset + ')'
  ;

stmt
  : wire
  | reg
  | 'mem' fid ':' info? INDENT memField* DEDENT
  | 'cmem' fid ':' ftype info?
  | 'smem' fid ':' ftype info?
  | mdir 'mport' fid '=' fid '[' exp ']' exp info?
  | instance
  | node
  | connect
  | fid 'is' 'invalid' info?
  | 'stop(' exp exp IntLit ')' info?
  | 'printf(' exp exp StringLit ( exp)* ')' info?
  | 'skip' info?
  ;

instance
  : 'inst' instance_id 'of' instance_of_id info?
  ;

instance_id
  : fid
  ;

instance_of_id
  : fid
  ;

connect
  : connected_lhs '<=' connected_rhs info?
  ;

connected_lhs
  : ref
  ;

connected_rhs
  : exp
  ;

node
  : 'node' node_id '=' node_val info?
  ;

node_id
  : fid
  ;

node_val
  : exp
  ;

wire
  : 'wire' wire_id ':' ftype info?
  ;

wire_id
  : fid
  ;

reg
  : 'reg' reg_id ':' ftype reg_clk (reg_reset)?
  ;

reg_id
  : fid
  ;

reg_clk
  : exp
  ;

reg_reset
  : 'with' ':' reset_block
  ;

memField
	:  'data-type' '=>' ftype NEWLINE
	| 'depth' '=>' IntLit NEWLINE
	| 'read-latency' '=>' IntLit NEWLINE
	| 'write-latency' '=>' IntLit NEWLINE
	| 'read-under-write' '=>' ruw NEWLINE
	| 'reader' '=>' fid+ NEWLINE
	| 'writer' '=>' fid+ NEWLINE
	| 'readwriter' '=>' fid+ NEWLINE
	;

simple_stmt
  : stmt | NEWLINE
  ;

info
  : FileInfo
  ;

mdir
  : 'infer'
  | 'read'
  | 'write'
  | 'rdwr'
  ;

ruw
  : 'old'
  | 'new'
  | 'undefined'
  ;

exp
  : const
  | ref
  | primop
  ;

ref
  : fid
  ;

const
  : 'UInt' '<' width '>' '(' const_ival ')'
  | 'SInt' '<' width '>' '(' const_ival ')'
  | 'UBits' '<' width '>' '(' const_bval ')'
  | 'SBits' '<' width '>' '(' const_bval ')'
  ;

const_ival
  : IntLit
  ;

const_bval
  : StringLit
  ;

// primop name includes open parenthesis
primop
  : primop_name op_argument*  op_parameter* ')'
  ;

op_argument
  : exp
  ;

op_parameter
  : IntLit
  ;

fid
  : Id
  | keyword
  ;

// I think this is just error detection
keyword
  : 'circuit'
  | 'module'
  | 'extmodule'
  | 'input'
  | 'output'
  | 'UInt'
  | 'SInt'
  | 'UBits'
  | 'SBits'
  | 'Clock'
  | 'flip'
  | 'wire'
  | 'reg'
  | 'with'
  | 'reset'
  | 'mem'
  | 'data-type'
  | 'depth'
  | 'read-latency'
  | 'write-latency'
  | 'read-under-write'
  | 'reader'
  | 'writer'
  | 'readwriter'
  | 'inst'
  | 'of'
  | 'node'
  | 'is'
  | 'invalid'
  | 'when'
  | 'else'
  | 'stop'
  | 'printf'
  | 'skip'
  | 'old'
  | 'new'
  | 'undefined'
  | 'mux'
  | 'validif'
  | 'cmem'
  | 'smem'
  | 'mport'
  | 'infer'
  | 'read'
  | 'write'
  | 'rdwr'
  ;

// Parentheses are added as part of name because semantics require no space between primop and open parentheses
// (And ANTLR either ignores whitespace or considers it everywhere)
primop_name
  : 'add('
  | 'sub('
  | 'mul('
  | 'div('
  | 'rem('
  | 'lt('
  | 'leq('
  | 'gt('
  | 'geq('
  | 'eq('
  | 'neq('
  | 'pad('
  | 'asUInt('
  | 'asSInt('
  | 'asClock('
  | 'shl('
  | 'shr('
  | 'dshl('
  | 'dshr('
  | 'cvt('
  | 'neg('
  | 'not('
  | 'and('
  | 'or('
  | 'xor('
  | 'andr('
  | 'orr('
  | 'xorr('
  | 'cat('
  | 'bits('
  | 'head('
  | 'tail('
  | 'mux('
  | 'validif('
  ;

/*------------------------------------------------------------------
 * LEXER RULES
 *------------------------------------------------------------------*/

IntLit
  : '0'
  | ( '+' | '-' )? [1-9] ( Digit )*
  | '"' 'h' ( HexDigit )+ '"'
  ;

fragment
Nondigit
  : [a-zA-Z_]
  ;

fragment
Digit
  : [0-9]
  ;

fragment
HexDigit
  : [a-fA-F0-9]
  ;

StringLit
  : '"' ('\\"'|.)*? '"'
  ;

FileInfo
  : '@[' ('\\]'|.)*? ']'
  ;

Id
  : IdNondigit
    ( IdNondigit
    | Digit
    )*
  ;

fragment
IdNondigit
  : Nondigit
  | [~!@#$%^*\-+=?/]
  ;

fragment COMMENT
  : ';' ~[\r\n]*
  ;

fragment WHITESPACE
	: [ \t,]+
	;

SKIP_
	: ( WHITESPACE | COMMENT ) -> skip
	;

NEWLINE
	:'\r'? '\n' ' '*
	;