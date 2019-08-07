"""
Enum-style module, defining known modes of `BackupError`.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

import errno as _errno

UNKNOWN = 0

SRC_NOT_EXIST = 11
SRC_IS_FILE = 12
SRC_IS_DIR = 13

OUT_NOT_EXIST = 21
OUT_IS_FILE = 22
OUT_IS_DIR = 23
OUT_CANT_DELETE = 23

all_types = {
	_k: _v for _k, _v in locals().items()
	if not (
		_k.startswith('_') or
		_k in {'all_types', }
	)
}  # type: _t.Dict[str, int]

__type_key_mappings = {
	_v: _k for _k, _v in all_types.iteritems()
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


__type_errno_mappings = {
	UNKNOWN: _errno.EPERM,

	SRC_NOT_EXIST: _errno.ENOENT,
	SRC_IS_FILE: _errno.ENOTDIR,
	SRC_IS_DIR: _errno.EISDIR,

	OUT_NOT_EXIST: _errno.ENOENT,
	OUT_IS_FILE: _errno.ENOTDIR,
	OUT_IS_DIR: _errno.EISDIR,
	OUT_CANT_DELETE: _errno.EBUSY,
}


def type_errno(
	type_value  # type: int
):
	try:
		return __type_errno_mappings[type_value]
	except KeyError:
		return __type_errno_mappings[UNKNOWN]
