__author__ = 'DRL'

try:
	# support type hints:
	from typing import *
except ImportError:
	pass

try:
	from enum import Enum
except ImportError as er_enum:
	import sys
	py_ver = sys.version_info[:2]  # (2, 7)
	if py_ver[0] >= 3 and py_ver[1] >= 4:  # 3.4+, but somehow enums don't exist
		raise ImportError(er_enum.message + " (though Python version is higher than 3.4)")

	pip_args = ['install', '--upgrade', 'enum34']
	try:
		import pip
		pip.main(pip_args)
	except AttributeError:
		from pip import _internal as pip_internal
		pip_internal.main(pip_args)
	from enum import Enum

from pprint import pprint as pp
import os as _os
from collections import namedtuple

_str_t = (str, unicode)


# region Register types and their properties

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
}  # type: Dict[Union[type(VsRegister), type(PsRegister)], bool]


class ShaderType(Enum):
	vert = 'Vertex'
	frag = 'Pixel/Fragment'

# endregion


LineData = namedtuple(
	'LineData',
	['op', 'args', 'comment']
)  # type: (Optional[str], Optional[Tuple[str]], Optional[str])

Range = namedtuple(
	'Range',
	['first', 'last']
)  # type: (int, int)

CodeBlock = namedtuple(
	'CodeBlock',
	['type', 'sm', 'first_line', 'last_line']
)  # type: (Optional[ShaderType], int, int, int)
ShaderLineRanges = namedtuple(
	'ShaderLineRanges',
	['pre_comment', 'code', 'post_comment']
)  # type: (Optional[Range], CodeBlock, Optional[Range])

vert_extensions = {
	'.vs', '.vs_1_0', '.vs_1_1', '.vs_1_2', '.vs_1_3', '.vs_1_4', '.vs_2_0', '.vs_2_5', '.vs_2_x', '.vs_3_0',
}
frag_extensions = {
	'.ps', '.ps_1_0', '.ps_1_1', '.ps_1_2', '.ps_1_3', '.ps_1_4', '.ps_2_0', '.ps_2_5', '.ps_2_x', '.ps_3_0',
}
in_extensions = {'.fx', '.cg', '.cgfx', '.asm'}.union(vert_extensions).union(frag_extensions)
out_ext = '.hlsl'


def _classify_line(
	line  # type: Union[str, unicode]
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
		args = (s.strip() for s in code.split())  # split by whitespaces...
		args = [s for s in args if s]  # ... and keep only non-empty strings
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
		return any(op.startswith(p) for p in _block_prefixes)

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
		for i in reversed(xrange(len(res_blocks) - 1)):  # from pre-last to first range
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

		for i_res in xrange(1, len(res_ranges)):  # skip the 1st one
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
		for i_res in xrange(len(res_ranges) - 1):  # skip the last one
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


def parse_file(file_path, print_path=False):
	"""
	Parse a single assembly file and convert it to an hlsl shader.
	"""
	if not _os.path.isfile(file_path):
		return

	if print_path:
		print 'Reading: ' + file_path

	# file_path = r'E:\1-Projects\SFM\_Tools\dx-shader-decompiler\ME-face-0.ps'

	base_path, ext = _os.path.splitext(file_path)
	ext = ext.lower()

	with open(file_path, 'r') as fl:
		lines = (_classify_line(l) for l in fl)
		lines = filter(None, lines)  # type: List[LineData]
	if not lines:
		return

	if print_path:
		print '\tParsing...' + file_path
	shader_ranges = _detect_shader_ranges(lines, ext)
	pp(shader_ranges)


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
		print '\nFiles in folder: ' + path
	for f in files:
		parse_file(f, print_paths)
	return


if __name__ == '__main__':
	import sys
	for p in sys.argv[1:]:
		parse(p, True)
	print '\nComplete'
	raw_input()
