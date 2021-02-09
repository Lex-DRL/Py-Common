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
from drl_common.py_2_3.enum import EnumDefault as __EnumDefault

_errno_all = frozenset(_errno.errorcode.values())


class BackupErrorType(__EnumDefault):
	"""Supported modes for ``BackupError``."""

	# default:
	UNKNOWN = 0  # type: BackupErrorType

	SRC_NOT_EXIST = 11  # type: BackupErrorType
	SRC_IS_FILE = 12  # type: BackupErrorType
	SRC_IS_DIR = 13  # type: BackupErrorType

	OUT_NOT_EXIST = 21  # type: BackupErrorType
	OUT_IS_FILE = 22  # type: BackupErrorType
	OUT_IS_DIR = 23  # type: BackupErrorType
	OUT_CANT_DELETE = 23  # type: BackupErrorType


__type_errno_map = {
	BackupErrorType.UNKNOWN: _errno.EPERM,

	BackupErrorType.SRC_NOT_EXIST: _errno.ENOENT,
	BackupErrorType.SRC_IS_FILE: _errno.ENOTDIR,
	BackupErrorType.SRC_IS_DIR: _errno.EISDIR,

	BackupErrorType.OUT_NOT_EXIST: _errno.ENOENT,
	BackupErrorType.OUT_IS_FILE: _errno.ENOTDIR,
	BackupErrorType.OUT_IS_DIR: _errno.EISDIR,
	BackupErrorType.OUT_CANT_DELETE: _errno.EBUSY,
}


def error_type_errno(
	error_type  # type: _t.Union[BackupErrorType, int]
):
	"""Get a corresponding errno for the given error-type."""
	return __type_errno_map[BackupErrorType.get(error_type)]


class BackupError(EnvironmentError):
	"""
	An error during backup process.
	"""

	# noinspection PyShadowingBuiltins
	def __init__(
		self,
		message='',  # type: _str_hint
		type=None,  # type: _t.Optional[_t.Union[BackupErrorType, int]]
		path=None,  # type: _t.Optional[_str_hint]
		errno=None  # type: _t.Optional[int]
	):
		"""
		:param message: The string passed as a `strerror` to the OS.
		:param type:
			The sub-type of an error. See ``BackupErrorType`` Enum.

			If omitted, the default **UNKNOWN** ``BackupErrorType`` is used.
		:param path: The path of a file/dir causing the error.
		:param errno:
			You can explicitly specify the error-number
			(from the built-in ``errno`` module).
			Otherwise, it will be automatically detected from the error type
			with ``error_type_errno()``, but it may be not the best match for
			your specific case.
		"""
		type = BackupErrorType.get(type)  # type: BackupErrorType
		if errno is None or errno not in _errno_all:
			errno = error_type_errno(type)
		super(BackupError, self).__init__(errno, message, path)
		self.__type = type

	@property
	def type(self):
		"""The sub-type of an error. See ``BackupErrorType`` Enum."""
		return self.__type


class BackupMode(__EnumDefault):
	"""
	Supported backup methods:
		* `REPLACE` - remove existing files/folders at the out path before backing up.
		* `SUBDIR_DATE` - create a sub-folder with the backup date.
		* `SUBDIR_VER` - create a sub-folder with an incrementing version number.
	"""

	# default:
	REPLACE = 1  # type: BackupMode

	SUBDIR_DATE = 2  # type: BackupMode
	SUBDIR_VER = 3  # type: BackupMode


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
	mode=None  # type: _t.Optional[_t.Union[BackupMode, int]]
):
	mode = BackupMode.get(mode)  # type: BackupMode
	src_path = _unix_p(_path.abspath(src_path))
