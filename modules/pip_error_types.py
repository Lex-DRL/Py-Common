"""
Enum-style module, defining known modes of PipError.
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


ALL_TYPES = {
	k: v for k, v in locals().iteritems()
	if not (
		k.startswith('_') or
		k in {'ALL_TYPES', }
	)
}  # type: _t.Dict[str, int]


__type_key_mappings = {
	v: k for k, v in ALL_TYPES.iteritems()
}  # type: _t.Dict[int, str]


def type_key(type_value):
	"""
	Get the human-readable name of given errortype-code.
	"""
	try:
		return __type_key_mappings[type_value]
	except KeyError:
		return __type_key_mappings[UNKNOWN]
