"""
High-level tools performing file backups.
"""
__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)

from os import path as _path
import errno as _errno

from drl_os import process as _prc
from . import modes, error_types

_errno_all = set(_errno.errorcode.itervalues())


class BackupError(EnvironmentError):
	"""
	An error during backup process.
	"""

	# noinspection PyShadowingBuiltins
	def __init__(
		self,
		message='',  # type: _str_hint
		type=None,  # type: _t.Optional[int]
		path=None,  # type: _t.Optional[_str_hint]
		errno=None  # type: _t.Optional[int]
	):
		"""
		:param message: The string passed as a `strerror` to the OS.
		:param type: The sub-type of an error. See `error_types` submodule.
		:param path: The path of a file/dir causing the error.
		:param errno:
			You can explicitly specify the error-number
			(from the built-in `errno` module).
			Otherwise, it will be automatically detected from the error type
			with `error_types.type_errno()`, but it may be not the best match for
			your specific case.
		"""
		if type not in error_types.all_types:
			type = error_types.UNKNOWN
		if errno is None or errno not in _errno_all:
			errno = error_types.type_errno(type)
		super(BackupError, self).__init__(errno, message, path)
		self.__type = type

	@property
	def type(self):
		"""The sub-type of an error. See `error_types` submodule."""
		return self.__type


# houdini has a bug disallowing to use '\\' directly. So:
_wrong_slash = 'z\\z'[1]
_right_slash = 'z/z'[1]


def _unix_p(
	pth  # type: _str_hint
):
	return pth.replace(_wrong_slash, _right_slash)


def copy_dir(
	src_path,  # type: _str_hint
	out_path,  # type: _str_hint
	mode=modes.REPLACE
):

	src_path = _unix_p(_path.abspath(src_path))
