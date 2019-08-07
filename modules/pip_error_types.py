"""
Enum-style module, defining known modes of `PipError`.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	import typing as _t
except ImportError:
	pass

CUSTOM = -1
UNKNOWN = 0
NO_PIP = 1
MODULE_CANT_IMPORT = 2


all_types = {
	_k: _v for _k, _v in locals().items()
	if not (
		_k.startswith('_') or
		_k in {'all_types', }
	)
}  # type: _t.Dict[str, int]


# for _k, _v in sorted(ALL_TYPES.iteritems()):
# 	print('{} => {}'.format(_k, _v))

__type_key_mappings = {
	v: k for k, v in all_types.iteritems()
}  # type: _t.Dict[int, str]


def type_key(
	type_value  # type: int
):
	"""
	Get the human-readable name of given errortype-code.
	"""
	try:
		return __type_key_mappings[type_value]
	except KeyError:
		return __type_key_mappings[UNKNOWN]
