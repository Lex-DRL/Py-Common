"""
Functions to perform pretty-formatted (indented) json both in py2 and py3.
"""

__author__ = 'Lex Darlog (DRL)'

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	str_t as _str_t,
	t_strict_unicode as _unicode,

	str_h as _str_h,
	str_h_o as _str_h_o,
	path_h as _path_h,
	path_h_o as _path_h_o,
)

# endregion

import re
import json
from collections import (
	OrderedDict as _OrderedDict,
	namedtuple as _namedtuple,
)


def __detect_str_indent_support():
	from sys import version_info
	major, minor = version_info[:2]
	return major >= 3 and minor >= 2


__is_str_indent_supported = __detect_str_indent_support()

try:
	__IndentReplacement = _t.NamedTuple(
		'_IndentReplacement', [
			('replace', bool),
			('indent', _t.Union[_str_h_o, int]),
			('str_indent', _str_h)
		]
	)
except:
	__IndentReplacement = _namedtuple('_IndentReplacement', ['replace', 'indent', 'str_indent'])


def __is_indent_replacement_needed(
	indent=2,
	tab=True,
):
	"""
	Detect, whether manual replacement should be done at all, and
	generate the proper values for the 'indent' arg sent to `json.loads()`, as well
	as `str_indent` that is the replacement (if so, indent will be 1).
	"""

	indent_is_int = isinstance(indent, int)

	if not(indent_is_int or indent is None):
		# indent is probably a string
		if not isinstance(indent, _str_t):
			try:
				indent = str(indent)
			except:
				try:
					indent = _unicode(indent)
				except:
					indent = repr(indent)
		if not indent:
			indent = 0
			indent_is_int = True
		else:
			indent_is_int = False

	assert isinstance(indent, int) == indent_is_int
	assert indent is None or indent_is_int or isinstance(indent, _str_t), (
		"'indent' must be None/int/string here. Got: {}".format(repr(indent))
	)

	if indent_is_int and indent < 0:
		indent = 0
	if not indent:
		# regardless of python version, no indents at all, so no replacements.
		return __IndentReplacement(False, indent, '')

	assert isinstance(indent, _str_t) != bool(indent_is_int), (
		"Here, 'indent' must be either int or str, and 'indent_is_int' reflect it. "
		"Got: {}, {}".format(repr(indent), indent_is_int)
	)

	if __is_str_indent_supported:
		# no need to do it ourselves, built-in json module can handle it already:
		if tab:
			indent = '\t'
		return __IndentReplacement(False, indent, '')

	if indent_is_int and not tab:
		# even in old python, no replacements since we use json in vanilla way:
		return __IndentReplacement(False, indent, '')

	# We're in py2; either we need to do tabs or indent is a string.

	if not indent_is_int:
		assert isinstance(indent, _str_t) and indent, (
			"'indent' must be non-empty string here. Got: {}".format(repr(indent))
		)
		return __IndentReplacement(True, 1, indent)

	# so, the only option left is using tabs
	assert bool(tab) and isinstance(indent, int) and indent > 0, (
		"'tab' must be enabled here, with non-zero int 'indent'. Got: {}, {}".format(
			tab, repr(indent)
		)
	)
	return __IndentReplacement(True, 1, '\t')


__re_indent = re.compile('^ +')


def dumps(
	data_obj,
	indent=2,  # type: _t.Union[_str_h_o, int]
	tab=True,
	**dump_args
):
	do_replacement, indent, str_indent = __is_indent_replacement_needed(indent, tab)
	dump_args['indent'] = indent
	res = json.dumps(data_obj, **dump_args)

	if not(do_replacement and res and str_indent):
		return res

	# perform manual indents replacement for old version of python

	def replace_indent(
		match,  # type: _t.Match
	):
		return str_indent * len(match.group())

	res_lines = (x.strip('\n\r') for x in res.split('\n'))
	res_lines = (__re_indent.sub(replace_indent, x) for x in res_lines)

	joiner = u'\n' if isinstance(res, _unicode) else '\n'
	return joiner.join(res_lines)


# legacy name:
prettify_obj = dumps


# TODO: fix: 1) remove trailing commas, 2) '-strings -> "-strings
# _map_blocks = {
# 	'(': ')',
# 	'{': '}',
# 	'[': ']',
# }
# _map_str = {
# 	'"': r'\"',
# 	"'": r"\'",
# }
#
#
# def __fix_trailing_commas_g(
# 	json_string,  # type: _str_h
# ):
# 	pass


def __load_args(
	load_args=None,  # type: _t.Optional[_t.Dict[str, _t.Any]]
):
	if load_args is None:
		load_args = dict()
	# keep items order in dict objects by default:
	if 'object_pairs_hook' not in load_args:
		load_args['object_pairs_hook'] = _OrderedDict
	return load_args


def loads(
	json_string,  # type: _str_h
	**load_args
):
	"""
	A wrapper on top of default `json.loads()`, which uses `OrderedDict`, unless
	`object_pairs_hook` argument is passed explicitly, with another callable.
	"""
	return json.loads(json_string, **__load_args(load_args))


def load(
	file_path,  # type: _str_h
	**load_args
):
	"""
	A wrapper on top of default `json.load()`, which uses `OrderedDict`, unless
	`object_pairs_hook` argument is passed explicitly, with another callable.
	"""
	with open(file_path, 'rb') as f:
		data_obj = json.load(f, **__load_args(load_args))
	return data_obj


def dump(
	data_obj,
	fp,
	indent=2,  # type: _t.Union[_str_h_o, int]
	tab=True,
	**dump_args
):
	"""
	A wrapper on top of default `json.load()`, which also
	prettifies the generated json string.
	"""
	json_string = dumps(
		data_obj, indent=indent, tab=tab, **dump_args
	)
	with open(fp, 'wb') as f:
		res = f.write(json_string)
	return res


def prettify_str(
	json_string,  # type: _str_h
	indent=2,  # type: _t.Union[_str_h_o, int]
	tab=True,
	load_args=None,  # type: _t.Optional[_t.Dict[str, _t.Any]]
	data_callback=None,  # type: _t.Optional[_t.Callable]
	**dump_args
):
	data_obj = json.loads(json_string, **__load_args(load_args))
	if data_callback is not None:
		data_obj = data_callback(data_obj)
	return dumps(
		data_obj, indent=indent, tab=tab, **dump_args
	)


def prettify_file(
	file_path,  # type: _path_h_o
	indent=2,  # type: _t.Union[_str_h_o, int]
	tab=True,
	load_args=None,  # type: _t.Optional[_t.Dict[str, _t.Any]]
	data_callback=None,  # type: _t.Optional[_t.Callable]
	**dump_args
):
	"""
	A wrapper on top of all the prettified functions, which sequentially performs
	read from the json file, calls an optional data callback and writes back
	to the same file.
	"""
	data_obj = loads(file_path, **load_args)
	if data_callback is not None:
		data_obj = data_callback(data_obj)
	return dump(data_obj, file_path, indent=indent, tab=tab, **dump_args)
