__author__ = 'DRL'

try:
	# support type hints in Python 3:
	from typing import *
except ImportError:
	pass

from drl_common.py_2_3.enum import Enum

from pprint import pprint as pp
import os as _os
import string as _str
import re as _re
from collections import namedtuple as _namedtuple

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_h as _str_h,
	t_strict_unicode as _unicode,
	izip as _izip,
	xrange as _xrange,
	raw_input as _input,
)


# region Enums

class VsRegister(Enum):
	"""
	Vertex-shader register types. Based on vs_3_0.

	:url: https://docs.microsoft.com/en-us/windows/desktop/direct3dhlsl/dx9-graphics-reference-asm-vs-registers-vs-3-0
	"""
	v = 'Input'
	r = 'Temporary'
	c = 'Constant Float'
	i = 'Constant Integer'
	b = 'Constant Boolean'
	s = 'Sampler'
	aL = 'Loop Counter'
	p = 'Predicate'

	a = 'Address'

	o = 'Output'


class PsRegister(Enum):
	"""
	Pixel-shader register types. Based on ps_3_0.

	:url: https://docs.microsoft.com/en-us/windows/desktop/direct3dhlsl/dx9-graphics-reference-asm-ps-registers-ps-3-0
	"""
	v = 'Input'
	r = 'Temporary'
	c = 'Constant Float'
	i = 'Constant Integer'
	b = 'Constant Boolean'
	s = 'Sampler'
	aL = 'Loop Counter'
	p = 'Predicate'

	vFace = 'Face'
	vPos = 'Position'

	oC = 'Output Color'
	oDepth = 'Output Depth'


try:
	AnyRegister = Union[VsRegister, PsRegister]
except NameError:
	# suppress an error in Python 2 with no 'typing' module
	pass


class ShaderType(Enum):
	vert = 'Vertex'
	frag = 'Pixel/Fragment'


class DataType(Enum):
	bool = 'Bool'
	int = 'Int'
	float = 'Float'
	sampler = 'Sampler'


class SamplerType(Enum):
	s2d = '2D'
	cube = 'Cube'
	volume = 'Volume'


all_shader_types = set(ShaderType)

vs_register_type = dict(VsRegister._member_map_)  # type: Dict[str, type(VsRegister)]
ps_register_type = dict(PsRegister._member_map_)  # type: Dict[str, type(PsRegister)]
register_type = {
	ShaderType.vert: vs_register_type,
	ShaderType.frag: ps_register_type
}  # type: Dict[ShaderType, Dict[str, AnyRegister]]

# Dictionary, determining dimensions of a given register (whether it's a vector4 or a scalar):
reg_vector4 = {
	VsRegister.v: True,
	VsRegister.r: True,
	VsRegister.c: True,
	VsRegister.i: True,
	VsRegister.b: False,
	VsRegister.s: True,
	VsRegister.aL: False,
	VsRegister.p: True,

	VsRegister.a: True,

	VsRegister.o: True,

	PsRegister.v: True,
	PsRegister.r: True,
	PsRegister.c: True,
	PsRegister.i: True,
	PsRegister.b: False,
	PsRegister.s: True,
	PsRegister.aL: False,
	PsRegister.p: False,

	PsRegister.vFace: False,
	PsRegister.vPos: True,

	PsRegister.oC: True,
	PsRegister.oDepth: False,
}  # type: Dict[AnyRegister, bool]

reg_data_type = {
	VsRegister.v: None,  # TODO V
	VsRegister.r: None,
	VsRegister.c: None,
	VsRegister.i: None,
	VsRegister.b: None,
	VsRegister.s: None,
	VsRegister.aL: None,
	VsRegister.p: None,

	VsRegister.a: None,

	VsRegister.o: None,  # TODO ^

	PsRegister.v: DataType.float,
	PsRegister.r: DataType.float,
	PsRegister.c: DataType.float,
	PsRegister.i: DataType.int,
	PsRegister.b: DataType.bool,
	PsRegister.s: DataType.sampler,
	PsRegister.aL: None,
	PsRegister.p: DataType.bool,

	PsRegister.vFace: None,
	PsRegister.vPos: None,

	PsRegister.oC: DataType.float,
	PsRegister.oDepth: DataType.float,
}  # type: Dict[AnyRegister, Optional[DataType]]

# endregion


# region Named Tuples and data classes

LineData = _namedtuple(
	'LineData',
	['op', 'args', 'comment']
)  # type: (Optional[str], Optional[Tuple[str]], Optional[str])

Range = _namedtuple(
	'Range',
	['first', 'last']
)  # type: (int, int)

CodeBlock = _namedtuple(
	'CodeBlock',
	['type', 'sm', 'first_line', 'last_line']
)  # type: (Optional[ShaderType], int, int, int)
ShaderLineRanges = _namedtuple(
	'ShaderLineRanges',
	['pre_comment', 'code', 'post_comment']
)  # type: (Optional[Range], CodeBlock, Optional[Range])


class RegisterVar(object):
	"""
	A data class containing meta-object that connects an ASM register to it's HLSL variable.
	"""
	def __init__(
		self,
		shader_type,  # type: ShaderType
		register,  # type: str
		registers_up_to=None,  # type: Union[None, int, str]
		# data_type,  # type: DataType
		var_name=None,  # type: Optional[str]
		is_vector4=True,
		partial_precision=False
	):
		super(RegisterVar, self).__init__()

		# shader_type = ShaderType.frag
		if shader_type not in all_shader_types:
			raise ValueError('shader_type is unsupported: ' + repr(shader_type))
		self.__shader_type = shader_type

		if not isinstance(register, str):
			raise TypeError('register has a wrong type. <str> expected, got: ' + repr(register))
		if not register:
			raise ValueError('empty string is given as register name')
		# register = 'aL'
		reg_literal = register.rstrip('0123456789')

		reg_i = register[len(reg_literal):]
		reg_i = int(reg_i) if reg_i else None
		try:
			reg_type = register_type[shader_type][reg_literal]
		except KeyError:
			raise ValueError(
				"Unknown {0} register type: {1}".format(shader_type.value, register)
			)
		self.__reg_type = reg_type
		self.__reg_name = register
		self.__reg_literal = reg_literal
		self.__reg_i = reg_i  # type: Optional[int]

		self.__reg_dt = reg_data_type[reg_type]  # type: Optional[DataType]

		self.__regs_to = RegisterVar.__check_up_to(registers_up_to, register, reg_literal, reg_i)

		self.__vector4 = bool(is_vector4)

		self.__var = RegisterVar.__check_var_name(var_name)

		self.__pp = bool(partial_precision)

	@staticmethod
	def __check_var_name(val):
		if not val:
			return None
		if not isinstance(val, str):
			raise TypeError("var_name has a wrong type. <str> expected, got: " + repr(val))
		if val[0] not in set('_' + _str.ascii_letters):
			raise ValueError(
				"var_name need to start from either upper/lower-case latin character or underscore. Got: " + repr(val)
			)
		return val

	@staticmethod
	def __check_up_to(
		val,  # type: Union[None, int, str]
		reg_str,  # type: str
		reg_literal,  # type: str
		reg_i  # type: Optional[int]
	):
		if val is None:
			return reg_i
		if reg_i is None:
			raise ValueError(
				"Can't set registers_up_to for a register that doesn't have in index. "
				"Register: {0}. Got: {1}".format(reg_str, repr(val))
			)
		assert isinstance(reg_i, int)
		if not isinstance(val, (int, str)):
			raise TypeError(
				"registers_up_to has a wrong type. Expected: (string) name or (int) index of the last register taken. Got: " +
				repr(val)
			)
		if isinstance(val, str):
			if not val.startswith(reg_literal):
				raise ValueError(
					"Can't set registers_up_to for {0} with different register type: {1}".format(
						reg_str, repr(val)
					)
				)
			val_id = val[len(reg_literal):]
			if not val_id:
				raise ValueError(
					"Can't set registers_up_to for {0} with no trailing register index: {1}".format(
						reg_str, repr(val)
					)
				)
			if val_id.strip('0123456789'):
				raise ValueError(
					"Can't set registers_up_to for {0} with an incorrectly named register: {1}".format(
						reg_str, repr(val)
					)
				)
			val = int(val_id)
		assert isinstance(val, int)
		if val < reg_i:
			raise ValueError(
				"Can't reduce registers_up_to for {0} from {1} to: {2}".format(reg_str, reg_i, val)
			)
		return val

	@property
	def shader_type(self):
		return self.__shader_type

	@property
	def register(self):
		return self.__reg_name

	@property
	def reg_type(self):
		return self.__reg_type

	@property
	def reg_literal(self):
		return self.__reg_literal

	@property
	def reg_index(self):
		return self.__reg_i

	@property
	def regs_to(self):
		"""
		The index of the last register in a range taken by this variable.

		Can be one of:
			* None if register isn't indexed.
			* Same as `reg_index` if only this register is taken
			* Greater than `reg_index` if the variable represents a matrix.
		"""
		return self.__regs_to

	@regs_to.setter
	def regs_to(self, value):
		self.__regs_to = RegisterVar.__check_up_to(
			value,
			self.__reg_name, self.__reg_literal, self.__reg_i
		)

	@property
	def data_type(self):
		return self.__reg_dt

	@property
	def is_vector4(self):
		return self.__vector4

	@is_vector4.setter
	def is_vector4(self, value):
		self.__vector4 = bool(value)

	@property
	def var_name(self):
		return self.__var

	@var_name.setter
	def var_name(self, value):
		self.__var = RegisterVar.__check_var_name(value)

	@property
	def partial_precision(self):
		return self.__pp

	@partial_precision.setter
	def partial_precision(self, value):
		self.__pp = bool(value)

	def __repr__(self):
		specifier = ' '.join([
			spec for spec, cond in (
				('PP', self.__pp),
				(
					self.__reg_dt.value if self.__reg_dt is not None else '',
					self.__reg_dt is not None
				),
				('vector' if self.__vector4 else 'scalar', True),
			) if cond
		])
		if specifier:
			specifier = ' [{0}]'.format(specifier)
		return '<RegisterVar {reg_lit}{reg_i}{specifier}{for_var}>'.format(
			specifier=specifier,
			reg_lit=self.__reg_literal,
			reg_i=(
				'' if self.__reg_i is None else (
					str(self.__reg_i)
					if self.__reg_i == self.__regs_to
					else '{0}-{1}'.format(self.__reg_i, self.__regs_to)
				)
			),
			for_var='' if not self.__var else " for '{0}'".format(self.__var)
		)


class DeclaredVar(object):
	"""
	Extracted from a preceding comment block.
	"""
	def __init__(
		self,
		name,  # type: Optional[str]
		array_size=None,  # type: Optional[int]
		type_str=None,  # type: Optional[str]
		comment=None,  # type: Optional[_str_h]
		register=None,  # type: Optional[str]
		regs_num=None  # type: Optional[int]
	):
		super(DeclaredVar, self).__init__()

		def cleaner_str(val):
			return str(val) if val else None

		self.name = cleaner_str(name)
		self.array_size = array_size  # type: int
		self.type_str = cleaner_str(type_str)
		self.comment = comment  # type: Optional[_str_h]
		self.register = cleaner_str(register)
		self.regs_num = regs_num  # type: Optional[int]

	def __repr__(self):
		return '<DeclaredVar: {tp} {nm}{arr}{reg}{comm}>'.format(
			tp=self.type_str if self.type_str else '??',
			nm=self.name if self.name else '????',
			arr='' if self.array_size is None else '[{0}]'.format(self.array_size),
			reg=' ({0})'.format(self.register) if self.register else '',
			comm=' //' if self.comment else ''
		)

# endregion


# region Predefined public vars

vert_extensions = {
	'.vs', '.vs_1_0', '.vs_1_1', '.vs_1_2', '.vs_1_3', '.vs_1_4', '.vs_2_0', '.vs_2_5', '.vs_2_x', '.vs_3_0', '.vs_3_5',
	'.vs_4_0', '.vs_4_5', '.vs_4_6', '.vs_5_0',
}
frag_extensions = {
	'.ps', '.ps_1_0', '.ps_1_1', '.ps_1_2', '.ps_1_3', '.ps_1_4', '.ps_2_0', '.ps_2_5', '.ps_2_x', '.ps_3_0', '.ps_3_5',
	'.ps_4_0', '.ps_4_5', '.ps_4_6', '.ps_5_0',
}
in_extensions = {'.fx', '.cg', '.cgfx', '.asm'}.union(vert_extensions).union(frag_extensions)
out_ext = '.hlsl'

# endregion


# region Functions splitting the lines list to a bunch of separate shader blocks

def _classify_line(
	line  # type: _str_h
):
	"""
	Generate the initial line's namedtuple.
	It's supposed to be called per-line during the main file read.
	"""
	line = line.strip()
	if not line:
		return None

	# line = '    def c16, 0.858085215, -0.858085215, 0.247708291, 0.429042608'

	line = line.split('//')
	code = line.pop(0)
	comment = '//' + '//'.join(line) if line else ''
	code = code.strip()
	comment = comment.strip()
	if not(code or comment):
		return None

	op = ''
	args = tuple()  # type: Tuple[str]

	if code:
		# split by whitespaces...
		args = (s.strip() for s in code.split())
		# ... and keep only non-empty strings:
		args = [s for s in args if s]  # type: List[str]
		op = args.pop(0)
		args = ' '.join(args).split(',')
		args = (s.strip() for s in args)
		args = tuple(s for s in args if s)  # type: Tuple[str]

	assert not(args and not op)

	if not(op or args or comment):
		return None

	if not op:
		op = None
	if not args:
		args = None
	if not comment:
		comment = None

	return LineData(op, args, comment)


_sm_map = {
	'vs': ShaderType.vert,
	'ps': ShaderType.frag
}
_block_prefixes = ('ps', 'vs')
_digit_str_set = set('0123456789')


def _detect_shader_ranges(
	lines,  # type: List[LineData]
	ext  # type: str
):
	"""
	Split one linear list of `LineData` items to independent 'shader blocks' -
	in case a single file has multiple blocks of ASM code inside it.

	Each shader block contains the following metadata (no actual lines):
		* pre-comment range (start/end), None if not present
		* the main code range as `CodeBlock`, also specifying the shader type and SM
		* post-comment range (start/end), None if not present
	"""
	if not lines:
		return None

	max_line_i = len(lines) - 1

	def is_block_start(
		line  # type: LineData
	):
		"""
		Roughly detect if the given line represents shader type and model declaration.
		Do so by simply matching the line prefix, so the test may be false-positive.
		"""
		if line.args or not line.op:
			return False
		op = line.op.lower()  # type: str
		return any(op.startswith(pref) for pref in _block_prefixes)

	def detect_shader_type(
		op  # type: str
	):
		"""
		The actual parse of the SM-line. It should be called only for those lines which pass a test by is_block_start().
		Now we do it precisely, so no false detections should occur.
		"""
		def res_typed(
			shader_type,  # type: Optional[ShaderType]
			shader_model  # type: int
		):
			"""
			Just a wrapper function to generate type hints in the returned value.
			"""
			return shader_type, shader_model

		sm = op.lower()

		# special case: when the whole string is simply 'vs' or 'ps':
		try:
			sm_op = _sm_map[sm]  # type: ShaderType
			return res_typed(sm_op, 0)
		except KeyError:
			pass  # just continue, it's a more general case

		sm = [s for s in sm.split('_') if s]
		if not sm:
			return res_typed(None, 0)

		sm_mode = sm.pop(0)  # should be 'vs' or 'ps'
		try:
			sm_mode = _sm_map[sm_mode]  # type: ShaderType
		except KeyError:
			return res_typed(None, 0)

		if not sm:
			return res_typed(sm_mode, 0)

		sm = tuple(
			(
				int(v)
				if len(v) == 1 and v in _digit_str_set
				else -1
			) for v in sm
		)
		if any(v == -1 for v in sm) or sm[0] < 1:
			return res_typed(None, 0)
		if len(sm) > 2:
			return res_typed(None, 0)

		if len(sm) == 1:
			sm = (sm[0], 0)

		assert (
			sm_mode and
			sm and
			all(v >= 0 for v in sm) and
			sm[0] > 0 and
			len(sm) == 2
		)

		sm = sm[0] * 10 + sm[1]
		return res_typed(sm_mode, sm)

	def continuous_code_blocks_sequence():
		"""
		Split the entire list of lines to the list of code ranges.
		These ranges may have incorrect comment-to-block association.
		But the result is guaranteed to be:
			* continuous. I.e., each next block starts at the next line after previous was ended.
			* the 1st block starting at line 0
			* the last block ending at the last line
			*
				all the blocks but the first one start with a shader-type specifier.
				I.e., 'ps_3_0'.
				These lines are actually what splits the original lines list.
			*
				If the shader type wasn't found in the whole list of lines,
				the func tries to detect it from the file extension.
			* If all attempts have failed, `None` is returned.
		"""
		def res_typed(
			res  # type: Optional[List[CodeBlock]]
		):
			return res

		res_blocks = (
			(l.op, i) for i, l in enumerate(lines)
			if is_block_start(l)
		)
		res_blocks = [
			CodeBlock(sm_i[0], sm_i[1], l_i, -1) for sm_i, l_i in (
				(detect_shader_type(op), i) for op, i in res_blocks
			) if sm_i[0]
		]
		if not res_blocks:
			# we haven't found vertex/pixel specification in the shader code itself.
			# let's try to detect it by a file extension:
			if ext and ext in vert_extensions:
				res_blocks = [CodeBlock(ShaderType.vert, 0, -1, -1)]
			elif ext and ext in frag_extensions:
				res_blocks = [CodeBlock(ShaderType.frag, 0, -1, -1)]
			else:
				# we couldn't even detect whether the shader is vertex or pixel
				return res_typed(None)

		# for the first and last block, snap ranges to the first/last line:
		block = res_blocks[0]
		res_blocks[0] = CodeBlock(block.type, block.sm, 0, block.last_line)
		block = res_blocks[-1]
		res_blocks[-1] = CodeBlock(block.type, block.sm, block.first_line, max_line_i)

		# generate range ends for intermediate ranges:
		next_range_start = res_blocks[-1].first_line
		for i in reversed(_xrange(len(res_blocks) - 1)):  # from pre-last to first range
			cur = res_blocks[i]  # type: CodeBlock
			cur = CodeBlock(cur.type, cur.sm, cur.first_line, next_range_start - 1)
			next_range_start = cur.first_line
			res_blocks[i] = cur
		return res_typed(res_blocks)

	def detect_comment_ranges():
		"""
		List of comment blocks specified as tuples of first and last line index for each block.
		"""
		in_comment = False
		comment_start = -1
		res_ranges = []  # type: List[Range]
		append = res_ranges.append
		for i, l in enumerate(lines):
			cur_is_comment = bool(l.comment) and not(l.op or l.args)
			if cur_is_comment == in_comment:
				# one more line either continuing comment or staying outside of it
				continue
			if cur_is_comment:
				# we've just entered a new comment block
				in_comment = True
				comment_start = i
				continue
			# we've just finished the comment block and currently are on the next line
			append(Range(comment_start, i-1))
			in_comment = False
		if in_comment and comment_start > -1:
			append(Range(comment_start, max_line_i))
		return res_ranges

	def shader_line_ranges(
		code_blocks_list,  # type: List[CodeBlock]
		comment_ranges_list  # type: List[Range]
	):
		"""
		Combine a list of code-blocks and of comment-ranges to a single continuous list of shader ranges,
		each containing:
			* pre-comment
			* the general code block
			* post-comment
		"""
		def res_typed(
			res  # type: List[ShaderLineRanges]
		):
			return res

		assert bool(code_blocks_list)
		res_ranges = res_typed(
			[ShaderLineRanges(None, c, None) for c in code_blocks_list]
		)
		if not comment_ranges_list:
			# no comment blocs, just return initial shader reanges intact:
			return res_ranges

		# we have some comment ranges.
		# we gonna update the res list by iteratively appending preceding comment ranges
		comment_ranges_left = comment_ranges_list[:]  # this will be modified, with ranges removed one by one
		first_code = res_ranges[0].code  # type: CodeBlock
		first_pre_c_ids = [
			i for i, cmt in enumerate(comment_ranges_left)
			if cmt.first == 0
		]
		if first_pre_c_ids:
			# found comment ranges starting from the 0 line,
			# attach them to the first shader-range:
			first_pre_c_ids = set(first_pre_c_ids)
			first_cmt_ranges = [
				cmt for i, cmt in enumerate(comment_ranges_left)
				if i in first_pre_c_ids
			]  # type: List[Range]
			comment_ranges_left = [
				cmt for i, cmt in enumerate(comment_ranges_left)
				if i not in first_pre_c_ids
			]  # type: List[Range]
			first_cmt_last_line = (
				max(cmt.last for cmt in first_cmt_ranges)
				if len(first_cmt_ranges) > 1
				else first_cmt_ranges[0].last
			)  # type: int
			res_ranges[0] = ShaderLineRanges(
				Range(0, first_cmt_last_line),
				CodeBlock(first_code.type, first_code.sm, first_cmt_last_line + 1, first_code.last_line),
				None
			)

		for i_res in _xrange(1, len(res_ranges)):  # skip the 1st one
			cur_code = res_ranges[i_res].code  # type: CodeBlock
			cur_start, cur_end = cur_code.first_line, cur_code.last_line  # type: int
			preceding_comments = [
				i for i, cmt in enumerate(comment_ranges_left)
				if cmt.last == cur_start-1
			]
			if not preceding_comments:
				continue

			if len(preceding_comments) == 1:
				pre_com_range = comment_ranges_left.pop(preceding_comments[0])
			else:
				# multiple preceding comments found, we need to combine their ranges
				# theoretically, this should never happen. But just in case...
				preceding_comments = set(preceding_comments)
				pre_ranges = [  # turn comment-range indices to the actual ranges...
					cmt for i, cmt in enumerate(comment_ranges_left) if i in preceding_comments
				]  # type: List[Range]
				comment_ranges_left = [  # ... and remove those ranges from the list
					cmt for i, cmt in enumerate(comment_ranges_left) if i not in preceding_comments
				]  # type: List[Range]
				range_min = min(pre_r.first for pre_r in pre_ranges)
				pre_com_range = Range(range_min, pre_ranges[0].last)

			# we've found the range of the preceding comp.
			# now we need to remove it from the previous code block ...
			prev_i = i_res - 1
			prev_res = res_ranges[prev_i]  # type: ShaderLineRanges
			prev_pre_c, prev_cd, prev_post_c = prev_res  # type: (Optional[Range], CodeBlock, None)
			prev_cd = CodeBlock(
				prev_cd.type, prev_cd.sm,
				prev_cd.first_line,
				min([prev_cd.last_line, pre_com_range.first - 1])
			)
			res_ranges[prev_i] = ShaderLineRanges(prev_pre_c, prev_cd, None)

			# ...and attach it to the current one as comment block:
			res_ranges[i_res] = ShaderLineRanges(pre_com_range, cur_code, None)

		# we've finished attaching comment blocks to their respective shader blocks.
		assert bool(res_ranges) and all(
			shd_r.post_comment is None
			for shd_r in res_ranges
		)
		if not any(shd_r.pre_comment for shd_r in res_ranges):
			# there are no comment blocks that can be identified as in-between shader code ranges,
			# so all of the comment ranges are None
			return res_ranges

		# so far, all of the post-comment should be none.
		# Let's check if we could populate them with some lines
		# from the next block's preceding comment:
		for i_res in _xrange(len(res_ranges) - 1):  # skip the last one
			next_i = i_res + 1
			next_block = res_ranges[next_i]  # type: ShaderLineRanges
			next_pre_c, next_cd, next_post_c = next_block  # type: (Optional[Range], CodeBlock, Optional[Range])
			if not next_pre_c:
				continue
			comment_line = lines[next_pre_c.first]
			if not(
				comment_line.comment.lower().startswith('// approximately ')
				and not comment_line.op
			):
				continue
			cur_block = res_ranges[i_res]  # type: ShaderLineRanges
			cur_pre_c, cur_cd, cur_post_c = cur_block  # type: (Optional[Range], CodeBlock, Optional[Range])
			cur_post_c = Range(next_pre_c.first, next_pre_c.first)
			trimmed_next_start = next_pre_c.first + 1
			if next_pre_c.last <= trimmed_next_start:
				next_pre_c = None
			else:
				next_pre_c = Range(trimmed_next_start, next_pre_c.last)

			res_ranges[i_res] = ShaderLineRanges(cur_pre_c, cur_cd, cur_post_c)
			res_ranges[next_i] = ShaderLineRanges(next_pre_c, next_cd, next_post_c)

		# we've processed post-comment for all the ranges but the last one.
		# do it now:
		last_comments = [
			cmt for cmt in comment_ranges_left
			if cmt.last == max_line_i
		]
		if last_comments:
			last_comment_start = min(cmt.first for cmt in last_comments)
			last_shd_range = res_ranges[-1]  # type: ShaderLineRanges
			last_pre, last_cd, last_post = last_shd_range  # type:  (Optional[Range], CodeBlock, Optional[Range])
			res_ranges[-1] = ShaderLineRanges(
				last_pre,
				CodeBlock(last_cd.type, last_cd.sm, last_cd.first_line, last_comment_start - 1),
				Range(last_comment_start, max_line_i)
			)
		return res_ranges

	# split all the lines to the blocks by 'ps_3_0' lines:
	code_blocks = continuous_code_blocks_sequence()
	if not code_blocks:
		return None

	# now let's detect ranges of comment blocks:
	comment_ranges = detect_comment_ranges()

	# now, let's combine comment and code ranges to split the entire file
	# to the actual shader blocks, with pre- and post-comments
	return shader_line_ranges(code_blocks, comment_ranges)

# endregion


# region Extract variable-to-register mappings from the preceding comment lines

_comment_prefix = '^\s*//[\s/]*'

_re_comment_empty = _re.compile('^\s*//[\s/_-]*$')

_re_params_start = _re.compile(
	_comment_prefix + 'parameters?[\W_]*$',  # '// Parameters:'
	flags=_re.IGNORECASE | _re.UNICODE
)
_re_var_decl = _re.compile(
	_comment_prefix +
	'('
	'(?:'
	'(?:bool|int|uint|dword|half|float|double|min10float|min16float|min12int|min16int|min16uint)'
	'(?:[2-4](?:x[2-4])?)?'  # match vectors and matrices: half[2/3/4[x2/3/4]]
	')|(?:'
	'sampler(?:1D|2D|3D|CUBE)?'
	')'
	')\s+('
	# match the var's name. Two cases: a single a-Z char or a longer name starting from [_a-zA-Z]:
	'(?:[_a-zA-Z]\w+)|(?:[a-zA-Z])'
	')(?:'
	# optional array size:
	'\s*\[(\d+)]'
	')?'
	# text of the optional comment-in-comment after the var declaration:
	'[\s;]*(?://\s*'
	'(.+)'
	')?$'
)
_re_regs_start = _re.compile(
	_comment_prefix + 'registers?[\W_]*$',  # '// Registers:'
	flags=_re.IGNORECASE | _re.UNICODE
)
_re_regs_title = _re.compile(
	_comment_prefix + 'names?[\s/]+reg(?:ister)?s?[\s/]+sizes?[-\s/_]*$',
	flags=_re.IGNORECASE | _re.UNICODE
)
_re_regs_mapping = _re.compile(
	_comment_prefix +
	'('
	# variable's name:
	'(?:[_a-zA-Z]\w+)|(?:[a-zA-Z])'
	')\s+('
	# register:
	'[cibs][0-9]+'
	')(?:'
	# optional size of the variable:
	'\s+([0-9]+)'
	')?[-\s_/]*$'
)


def _extract_var_names(
	comment_lines  # type: List[_str_h]
):
	"""
	Try to detect the original names of registers from the block of comments.

	:return:
		* list of detected mappings
		* modified comment_lines list, with all used mappings removed
	"""

	vars_list = list()  # type: List[DeclaredVar]

	if not comment_lines:
		return vars_list, comment_lines

	def first_true_index(
		values  # type: Iterable
	):
		"""
		Find the index of a first item which value is `True` when converted to `bool`.
		"""
		for i, val in enumerate(values):
			if val:
				return i
		return -1

	def last_true_index(
		values  # type: Union[List, Tuple]
	):
		for i in reversed(_xrange(len(values))):
			if values[i]:
				return i
		return -1

	# first, extract the block of param definitions:
	matches = tuple(
		_re_var_decl.match(l) for l in comment_lines
	)
	assert matches
	start_line = first_true_index(matches)
	if start_line > -1:
		# we already have all the vars' data so we're free to filter matches out,
		# at the same time splitting the block to a "pre-matches" and "whatever is left" part:
		comment_lines = [  # first, let's mark those lines we need to keep
			(not is_var, l) for is_var, l
			in _izip(matches, comment_lines)
		]  # type: List[Tuple[bool, str]]
		# and now let's split and filter:
		pre_block = [
			l for is_l, l in comment_lines[:start_line] if is_l
		]  # type: List[_str_h]
		comment_lines = [
			l for is_l, l in comment_lines[start_line:] if is_l
		]  # type: List[_str_h]

		# remove any lines related to the block from the pre-block and combine it with left comment_lines:
		if pre_block:
			# if we remove trailing comment lines and the "Parameters:" line,
			# which is the last line we need to keep:
			start_line = last_true_index([
				not(_re_comment_empty.match(l) or _re_params_start.match(l))
				for l in pre_block
			])
			if start_line > -1:
				pre_block = pre_block[:start_line+1]
				comment_lines = pre_block + comment_lines  # type: List[_str_h]

		vars_list = [
			DeclaredVar(
				nm,
				int(sz) if sz else None,
				tp_str,
				c
			) for tp_str, nm, sz, c in (
				v.groups() for v in matches if v
			)
		]

	# now, let's try to detect shaderVar-to-register mappings:
	shared = type('Shared', (object,), dict())
	shared.found_title = False
	shared.found_names = False
	shared.stage = 0
	shared.start = -1  # block first line index
	shared.end = -1  # the 1st line after the block
	shared.perfect_match_from = -1

	def match_as_reg_mapping(
		line,  # type: _str_h
		line_i  # type: int
	):
		"""
		A function that generates a match object for lines
		inside the shaderVar-to-register mapping block.

		This cannot be done as a simple expression in list comprehension
		because this function needs to remember which stage we are at:
		whether we have already entered and if we have got out of this block.

		Stages:
			* 0 - haven't entered the block yet
			* 1 - in block
			* 2 - left the block already
		"""

		stage = shared.stage
		if stage > 1:
			# we have already passed the block
			return None
		if not line or _re_comment_empty.match(line):
			# just skip empty lines
			return None
		if _re_regs_start.match(line):
			if stage < 1:
				shared.stage = 1
				shared.start = line_i
			shared.found_title = True
			return None
		if _re_regs_title.match(line):
			if stage < 1:
				shared.stage = 1
				shared.start = line_i
			shared.found_names = True
			return None

		match = _re_regs_mapping.match(line)
		if match:
			if shared.perfect_match_from < 0:
				if shared.found_title and shared.found_names:
					shared.perfect_match_from = line_i
			if stage < 1:
				shared.stage = 1
				shared.start = line_i
			return match

		# we get here only in one case: it's an arbitrary
		# non-empty comment which doesn't match the mapping pattern.
		if shared.stage == 1:
			shared.stage = 2
			shared.end = line_i
		return None

	matches = tuple(match_as_reg_mapping(l, i) for i, l in enumerate(comment_lines))
	assert matches
	assert shared.perfect_match_from >= shared.start

	if shared.perfect_match_from > -1 and any(matches[shared.start:shared.perfect_match_from]):
		# crop the false start
		shared.start = shared.perfect_match_from
	if shared.stage == 1:
		# the last line is also the end of block, we haven't exited it yet.
		shared.end = len(comment_lines) + 1
	if shared.start > shared.end:
		shared.start = shared.end

	if shared.start < 0 or shared.end < 0 or not any(matches[shared.start:shared.end]):
		# no mappings found, return whatever vars_list we already have detected (if any)
		return vars_list, comment_lines

	# cleanup any false matches me may have:
	matches = tuple(
		(m if shared.start <= i < shared.end else None)
		for i, m in enumerate(matches)
	)
	comment_lines = [
		l for i, (do_m, l) in enumerate(_izip(matches, comment_lines))
		if not do_m and (i < shared.start or i >= shared.end)
	]  # type: List[_str_h]
	matches = (m.groups() for m in matches if m)

	if not vars_list:
		# we haven't found any declarations, let's at least return mappings:
		vars_list = [
			DeclaredVar(
				nm,
				register=reg,
				regs_num=int(sz) if sz else None
			) for nm, reg, sz in matches
		]
		return vars_list, comment_lines

	# we have found both declarations and mappings.
	# we need to combine them
	vars_dict = {var.name: var for var in vars_list}  # type: Dict[str, DeclaredVar]

	def get_var(
		name  # type: str
	):
		if name in vars_dict:
			return vars_dict[name]
		new_var = DeclaredVar(name)
		vars_list.append(new_var)
		vars_dict[name] = new_var
		return new_var

	for nm, reg, sz in matches:
		var = get_var(nm)
		var.register = reg
		var.regs_num = int(sz) if sz else None

	return vars_list, comment_lines

# endregion


def _hlsl_code(
	shader_type,  # type: ShaderType
	shader_model,  # type: int  # not used yet 'cause the script only handles SM 3.0, could be anything for now
	pre_comments,  # type: List[str]
	code_lines,  # type: List[LineData]
	post_comments  # type: List[str]
):
	"""
	The main function which actually performs ASM->HLSL code conversion.
	It takes lines as multiple arguments, pre-processed to detect their grouping
	and in-line basic structure. And therefore is called from the other, higher-level func.
	All the arguments are mandatory, but empty lists or zero SM can be provided.

	:param shader_model: integer representing SM multiplied by 10. I.e., 14, 20, 30, 35
	"""

	error_start = '// ERROR ASM-> HLSL: '

	if not(shader_type and shader_type in all_shader_types):
		return [error_start + 'Unknown shader type']

	res = list()  # type: List[str]

	# TODO

	# TODO 1: detect metadata (var names and types) from the pre-comment block

	return res


def parse_file(file_path, print_path=False):
	"""
	Parse a single assembly file and convert it to an hlsl shader.
	"""
	if not _os.path.isfile(file_path):
		return

	if print_path:
		print('Reading: ' + file_path)

	# file_path = r'E:\1-Projects\SFM\_Tools\dx-shader-decompiler\ME-face-0.ps'

	base_path, ext = _os.path.splitext(file_path)
	ext = ext.lower()

	with open(file_path, 'r') as fl:
		lines = (_classify_line(l) for l in fl)
		lines = filter(None, lines)  # type: List[LineData]
	if not lines:
		return

	if print_path:
		print('\tParsing... ' + file_path)
	shader_ranges = _detect_shader_ranges(lines, ext)
	hlsl_shaders = []  # type: List[List[str]]
	for pre_c_r, code_r, post_c_r in shader_ranges:  # type: (Optional[Range], CodeBlock, Optional[Range])
		pre_comments = (
			[l.comment for l in lines[pre_c_r.first:pre_c_r.last+1]]
			if pre_c_r
			else list()
		)  # type: List[str]

		post_comments = (
			[l.comment for l in lines[post_c_r.first:post_c_r.last+1]]
			if post_c_r
			else list()
		)  # type: List[str]

		shader_type, shader_model, code_first, code_last = code_r  # type: (ShaderType, int, int, int)
		hlsl_shaders.append(
			_hlsl_code(shader_type, shader_model, pre_comments, lines[code_first:code_last+1], post_comments)
		)
	del lines


def is_proper_input_file(file_path):
	"""
	Whether the given file path seems to be an HLSL-assembly file.
	"""
	if not _os.path.isfile(file_path):
		return False
	# file_path = r'E:\1-Projects\SFM\_Tools\dx-shader-decompiler\ME-face-1.ps'
	ext = _os.path.splitext(file_path)[-1]  # type: str
	return (not ext) or ext.lower() in in_extensions


def parse(path, print_paths=False):
	if not _os.path.isdir(path):
		parse_file(path, print_paths)
		return

	files = [_os.path.join(path, f) for f in _os.listdir(path)]
	files = filter(is_proper_input_file, files)
	if print_paths and files:
		print('\nFiles in folder: ' + path)
	for f in files:
		parse_file(f, print_paths)
	return


if __name__ == '__main__':
	import sys
	for p in sys.argv[1:]:
		parse(p, True)
	print('\nComplete')
	_input()
