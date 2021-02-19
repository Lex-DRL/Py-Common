"""Version-independent type hints for string/unicode."""

__author__ = 'Lex Darlog (DRL)'
__all__ = (
	'str_t', 'str_hint', 'str_h',
	't_strict_str', 't_strict_unicode',
)

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as __t
	__tp = __t.Type
	__tpl = __t.Tuple
except ImportError:
	pass


# noinspection PyBroadException,PyPep8
try:
	t_strict_unicode = unicode
	t_strict_str = str
except:
	t_strict_unicode = str
	t_strict_str = bytes


# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	str_t = (str, unicode)
except:
	str_t = (bytes, str)


# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	str_hint = __t.Union[str, unicode]
except:
	# noinspection PyBroadException,PyPep8
	try:
		# noinspection PyUnresolvedReferences
		str_hint = __t.Union[bytes, str]
	except:
		str_hint = str

str_h = str_hint
