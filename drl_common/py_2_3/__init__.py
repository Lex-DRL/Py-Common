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

if py3:
	izip = zip
	izip_longest = zip_longest
	str_t = (str,)
else:
	from itertools import izip, izip_longest
	str_t = (str, unicode)

try:
	union_str = typing.Union[str, unicode]
except (NameError, AttributeError):
	union_str = None
