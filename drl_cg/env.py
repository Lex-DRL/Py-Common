"""
"""

__author__ = 'Lex Darlog (DRL)'

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	str_t as _str_t,
	str_hint as _str_h,
)

# endregion

import os as _os
from os import path as _pth
import errno as _errno


def _clean(
	path,  # type: _str_h
	is_file=False,
	is_dir=False,
	exists=False,
	raise_error=False,
):
	"""
	Clean-up a path:

		* make sure path has unix-style slashes
		* without any triling slashes
		* (optionally) make sure it actually exists as a file/dir/whatever

	:param path: the actual path
	:param is_file: make sure the path exists and points to a file
	:param is_dir: make sure the path exists and points to a directory
	:param exists: make sure the path exists
	:param raise_error:
		What to do if any of above checks is active and path doesn't exist:
			* `True` - raise a corresponding `OSError`.
			* `False` - just return an empty string.
	:return:
	"""
	if isinstance(path, _str_t):
		path = path.replace('\\', '/').rstrip('/')
	else:
		path = ''

	if not path:
		if raise_error:
			errno = _errno.ENOENT
			raise OSError(errno, _os.strerror(errno), path)
		return ''

	if is_file:
		if not _pth.isfile(path):
			if raise_error:
				errno = _errno.EISDIR if _pth.exists(path) else _errno.ENOENT
				raise OSError(errno, _os.strerror(errno), path)
			return ''
		return path

	if is_dir:
		if not _pth.isdir(path):
			if raise_error:
				errno = _errno.ENOTDIR if _pth.exists(path) else _errno.ENOENT
				raise OSError(errno, _os.strerror(errno), path)
			return ''
		return path

	if exists:
		if not _pth.exists(path):
			if raise_error:
				errno = _errno.ENOENT
				raise OSError(errno, _os.strerror(errno), path)
			return ''
		return path

	return path


DRL_CG_PATH = _clean(
	_os.environ.get('DRL_CG_PATH', 'C:/1-CG'),
	is_dir=True
)
