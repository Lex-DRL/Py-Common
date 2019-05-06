__author__ = 'DRL'

py2 = False
py3 = False

try:
	# support type hints:
	import typing
	py3 = True
except ImportError:
	import __empty_module as typing
	py2 = True
	py3 = False

try:
	from itertools import izip, izip_longest
except ImportError:
	izip = zip
	izip_longest = zip_longest


str_t = [str]
# noinspection PyBroadException,PyPep8
try:
	if unicode not in str_t:
		str_t += [unicode]
except:
	pass
# noinspection PyBroadException,PyPep8
try:
	if bytes not in str_t:
		str_t += [bytes]
except:
	pass
str_t = tuple(str_t)  # type: typing.Tuple[typing.Type[str], typing.Type[unicode]]

# noinspection PyBroadException,PyPep8
try:
	t_strict_unicode = unicode
	t_strict_str = str
except:
	t_strict_unicode = str
	t_strict_str = bytes

str_hint = str
# noinspection PyBroadException,PyPep8
try:
	str_hint = typing.Union[str_hint, unicode]
except:
	pass
# noinspection PyBroadException,PyPep8
try:
	str_hint = typing.Union[str_hint, bytes]
except:
	pass
# noinspection PyBroadException,PyPep8
try:
	str_hint = typing.Union[str_hint, typing.AnyStr]
except:
	pass
