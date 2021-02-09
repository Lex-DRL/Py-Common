from .py_2_3 import (
	typing as _t,
	str_t,
	str_hint,
	izip,
)
import collections as _c

__author__ = 'DRL'


def common_prefix(
	strings,  # type: _t.Sequence[str_hint]
	ignore_case=False
):
	"""
	Find the longest common prefix of multiple strings. I.e.:
		* 'aaa/bbb/ccc/111'
		* 'aaa/bbb/ccc/222'
		* 'aaa/bbb/ddd/222'

	-> 'aaa/bbb/'

	If `ignore_case` is `True`, the substring is extracted from the 1st string.
	"""
	if isinstance(strings, str_t):
		return strings
	if not strings:
		return ''
	if len(strings) < 2:
		return strings[0]

	# work with a copy of strings sequence:
	ss = [s.lower() for s in strings] if ignore_case else strings

	# fast-check if all the strings are equal:
	all_equal = True
	ss_rest = iter(ss)
	s0 = next(ss_rest)
	for s in ss_rest:
		if s0 != s:
			all_equal = False
			break
	if all_equal:
		return strings[0]

	common = 0
	for i, char_tuple in enumerate(izip(*ss)):
		chars_rest = iter(char_tuple)
		c0 = next(chars_rest)
		if not all(c0 == c for c in chars_rest):
			common = i
			break
	return strings[0][:common]


def error_if_not_str(var, var_name="variable"):
	if not isinstance(var_name, str_t) or not var_name:
		var_name = "variable"
	if not isinstance(var, str_t):
		raise Exception(
			'The {0} needs to be a string or unicode. Got: {1}'.format(var_name, repr(var))
		)


def to_str(item):
	"""
	Service function which turns everything to a printable string.

	The string/unicode object stays as is, anything else is turned to a string
	with repr().
	"""
	return item if isinstance(item, str_t) else repr(item)


def list_with_and(
	iterable,  # type: _t.Iterable
	and_sep=' and '  # type: str_hint
):
	"""
	The alternative to ', '.join(iterable), which generates a more human-like
	sequence. I.e., the last element is attached with an "and" separator.
	"""
	if not iterable:
		return ''

	if not isinstance(iterable, _c.Sequence):
		iterable = list(iterable)
	try:
		last = iterable[-1]
	except IndexError:
		return ''

	iterable = iterable[:-1]
	try:
		prefix = ', '.join(to_str(x) for x in iterable)
	except UnicodeError:
		prefix = u', '.join(to_str(x) for x in iterable)

	if not prefix:
		return last

	return prefix + and_sep + last
