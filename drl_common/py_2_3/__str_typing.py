"""Version-independent type hints for string/unicode."""

__author__ = 'Lex Darlog (DRL)'
__all__ = [
	'str_t', 'str_hint',
	't_strict_str', 't_strict_unicode',
]

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


str_t = [str]
# noinspection PyBroadException,PyPep8
try:
	if unicode not in str_t:
		str_t = [str, unicode]
except:
	pass
# noinspection PyBroadException,PyPep8
try:
	if bytes not in str_t:
		str_t = [bytes, str]
except:
	pass
str_t = tuple(str_t)  # type: __tpl[__tp[t_strict_str], __tp[t_strict_unicode]]


# noinspection PyBroadException,PyPep8
try:
	str_hint = __t.Union[str, unicode]
except:
	# noinspection PyBroadException,PyPep8
	try:
		str_hint = __t.Union[str, bytes]
	except:
		str_hint = str

# noinspection PyBroadException,PyPep8
# try:
# 	str_hint = typing.Union[str_hint, typing.AnyStr]
# except:
# 	pass
