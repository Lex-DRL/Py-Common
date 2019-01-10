__author__ = 'DRL'

py2 = False
py3 = False

try:
	# support type hints:
	import typing
	py3 = True
except ImportError:
	import __empty_module as typing
	py3 = False
	py2 = True

if py3:
	str_t = (str,)
else:
	str_t = (str, unicode)

try:
	union_str = typing.Union[str, unicode]
except (NameError, AttributeError):
	pass
