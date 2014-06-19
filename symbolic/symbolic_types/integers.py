#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Updated by Thomas Ball (2014)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import ast
from symbolic_type import SymbolicType
import symbolic.z3_wrap as z3

import sys

def correct(value, bits, signed):
    base = 1 << bits
    value %= base
    return value - base if signed and value.bit_length() == bits else value

char, word, dword, qword, byte, sword, sdword, sqword = (
    lambda v: correct(v, 8, True), lambda v: correct(v, 16, True),
    lambda v: correct(v, 32, True), lambda v: correct(v, 64, True),
    lambda v: correct(v, 8, False), lambda v: correct(v, 16, False),
    lambda v: correct(v, 32, False), lambda v: correct(v, 64, False))

#   MISSING: Mod | Pow  | FloorDiv, and much more...

def wrap(o):
	return lambda l,r : SymbolicInteger("se",ast.BinOp(left=l, op=o(), right=r))

class SymbolicInteger(SymbolicType):
	def __init__(self, name, expr=None):
		SymbolicType.__init__(self, name, expr)
		self.concrete_value = 0L
		if expr == None:
			self.z3_var = z3.newIntegerVariable(self.name)

	def __repr__(self):
		if self.isVariable():
			return self.name + "#" + str(self.concrete_value)
		else:
			return SymbolicType.__repr__(self)

	def getSymVariable(self):
		if self.isVariable():
			return [(self.name, self, self.z3_var)]
		else:
			return SymbolicType._getSymVariables(self,self.expr)

	def getExprConcr(self):
		if self.isVariable():
			return (self, self.getConcrValue())
		else:
			return SymbolicType.getExprConcr(self)

	# Integer results only from now on... :(
	# also, non-standard interpretation of Python integers
	
	def __add__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x+y), wrap(ast.Add))
	def __radd__(self,other):
		return self.__add__(other)

	def __sub__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x - y), wrap(ast.Sub))
	def __rsub__(self,other):
		return self.__sub__(other)

	def __mul__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x*y), wrap(ast.Mult))
	def __rmul__(self,other):
		return self.__mul__(other)

	def __and__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x & y), wrap(ast.BitAnd))
	def __rand__(self,other):
		return self.__and__(other)

	def __or__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x | y), wrap(ast.BitOr))
	def __ror__(self,other):
		return self.__or__(other)

	def __xor__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x ^ y), wrap(ast.BitXor))
	def __rxor__(self,other):
		return self.__xor__(other)

	def __lshift__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x << y), wrap(ast.LShift))
	def __rlshift__(self,other):
		return self.__lshift__(other)

	def __rshift__(self, other):
		return self._do_bin_op(other, lambda x, y: sdword(x >> y), wrap(ast.RShift))
	def __rrshift__(self,other):
		return self.__rshift__(other)

