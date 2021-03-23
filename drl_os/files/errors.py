__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
	str_h_o as _str_h_o,
	t_strict_unicode as _uni,
	path_t as _path_t,
	path_h as _path_h,
	path_h_o as _path_h_o,
)

import os as _os
import errno as _errno
from os import strerror as _err_str


def default_oserror(errno, message=None, path=None):
	"""
	Creates an `OSError` with the default message for the given errno.
	The first optional argument is the error's path.
	"""
	if not message:
		if errno in _errno.errorcode:
			message = _os.strerror(errno)
		else:
			message = ''
	return OSError(errno, message, path)


class _FilesystemBaseError(OSError):
	"""
	Base class for filesystem-related errors, a simple wrapper for the `IOError`.

	The only reasons why this class exists are:
		* it can build a new error from another `OSError` given as a 1st argument
		*
			it performs some automatic type conversion for input arguments
			(in case exception itself is constructed incorrectly)
		* it lets us catch more specific errors
		* it auto-generates the default error string if none is given
	"""
	def __init__(
		self,
		err_num,  # type: _t.Union[int, OSError]
		filename=None,  # type: _path_h_o
		err_str=None  # type: _str_h_o
	):
		if isinstance(err_num, OSError):
			filename = err_num.filename if (filename is None) else filename
			err_str = err_num.strerror if (err_str is None) else err_str
			err_num = err_num.errno

		num_msg = ''
		if err_num is None:
			err_num = -1
			num_msg = ' (no errno given)'
		if isinstance(err_num, (float, bool)):
			err_num = int(err_num)

		if not isinstance(err_num, int):
			num_msg = ' (wrong errno given: {0})'.format(repr(err_num))
			err_num = -1

		err_str = _FilesystemBaseError._check_str_arg(err_str)
		# filename = _check_str_arg(filename)

		if not err_str:
			err_str = _err_str(err_num)
		err_str += num_msg

		if filename is None:
			super(_FilesystemBaseError, self).__init__(err_num, err_str)
		else:
			super(_FilesystemBaseError, self).__init__(err_num, err_str, filename)

	@staticmethod
	def _check_str_arg(arg):
		if arg is None:
			return ''
		if not isinstance(arg, _path_t):
			if arg:
				try:
					return str(arg)
				except:
					try:
						return _uni(arg)
					except:
						return ''
			else:
				return ''
		return arg

	def __eq__(self, other):
		if not isinstance(other, IOError):
			return False
		return (
			self.errno == other.errno and
			self.filename == other.filename
		)

	def __ne__(self, other):
		return not self.__eq__(other)


class NotExist(_FilesystemBaseError):
	"""
	Given path doesn't exist.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		super(NotExist, self).__init__(_errno.ENOENT, filename, err_str)


class EmptyPath(NotExist):
	"""
	Empty path provided.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'The path is empty'
		super(EmptyPath, self).__init__(filename, err_str)


class NotDir(_FilesystemBaseError):
	"""
	Given path is not a folder.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		super(NotDir, self).__init__(_errno.ENOTDIR, filename, err_str)


class NotFile(_FilesystemBaseError):
	"""
	Given path is not a file.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'Not a file'
		super(NotFile, self).__init__(_errno.EISDIR, filename, err_str)


class NotReadable(_FilesystemBaseError):
	"""
	Given file/folder is not readable.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'File/folder is not readable'
		super(NotReadable, self).__init__(_errno.EACCES, filename, err_str)


class NotWriteable(_FilesystemBaseError):
	"""
	Given file/folder is not writeable.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'File/folder is not writeable'
		super(NotWriteable, self).__init__(_errno.EACCES, filename, err_str)


class UnknownObject(_FilesystemBaseError):
	"""
	The given path is neither a file nor a folder.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'Path is neither a file nor a folder'
		super(UnknownObject, self).__init__(_errno.ENOSYS, filename, err_str)


class PathAlreadyExist(_FilesystemBaseError):
	"""
	Unsuccessful attempt to overwrite a file/folder.

	In other words, you're trying to create a folder/file that already exist at the given path.

	:param overwrite:
		Whether you tried to overwrite the file first. I.e.:
			*
				`None`: it's unknown if this error happened because you just disabled overwrite
				or because it just can't be overwritten.
			* `0/False`: You're trying to add a folder/file at the path that already exist, and you didn't try to overwrite it.
			* `1/True`: You tried to overwrite the path first, but you can't do that for unknown reason.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		overwrite=None,  # type: _t.Union[None, int, bool]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'Path already exists'
		if not (overwrite is None):
			err_str += ' (overwrite=<{0}>)'.format(overwrite)
		super(PathAlreadyExist, self).__init__(_errno.EEXIST, filename, err_str)
		self.overwrite = overwrite


class FileAlreadyExist(PathAlreadyExist):
	"""
	An attempt to create/write a file that already exist.

	:param overwrite:
		Whether you tried to overwrite the file first. I.e.:
			*
				`None`: it's unknown if this error happened because you just disabled overwrite
				or because it just can't be overwritten.
			* `0/False`: You're trying to add a folder/file at the path that already exist, and you didn't try to overwrite it.
			* `1/True`: You tried to overwrite the path first, but you can't do that for unknown reason.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		overwrite=None,  # type: _t.Union[None, int, bool]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'File already exists'
		super(FileAlreadyExist, self).__init__(filename, overwrite, err_str)


class ParentFolderIsFile(PathAlreadyExist):
	"""
	An attempt to call a file while one of it's breadcrumb folders is a file itself.

	:param parent_folder: Optional path to a folder which turned out to be a file.
	:param overwrite:
		Whether you tried to overwrite the file first. I.e.:
			*
				`None`: it's unknown if this error happened because you just disabled overwrite
				or because it just can't be overwritten.
			* `0/False`: You're trying to add a folder/file at the path that already exist, and you didn't try to overwrite it.
			* `1/True`: You tried to overwrite the path first, but you can't do that for unknown reason.
	"""
	def __init__(
		self,
		filename=None,  # type: _t.Union[None, str, _uni]
		parent_folder=None,  # type: _t.Union[None, str, _uni]
		overwrite=None,  # type: _t.Union[None, int, bool]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		err_str = _FilesystemBaseError._check_str_arg(err_str)
		if not err_str:
			err_str = 'Parent folder is a file'
		if not (parent_folder is None):
			if not isinstance(parent_folder, (str, _uni)):
				try:
					parent_folder = str(parent_folder)
				except:
					parent_folder = _uni(parent_folder)
			err_str += ' (folder: "{0}")'.format(parent_folder)
		super(ParentFolderIsFile, self).__init__(filename, overwrite, err_str)
		self.parent_folder = parent_folder
