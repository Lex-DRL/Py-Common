__author__ = 'DRL'

try:
	# support type hints in Python 3:
	import typing as _t
except ImportError:
	pass

try:
	_uni = unicode  # Python 2
except NameError:
	_uni = str  # fix for Python 3

import errno
from os import strerror as _err_str


class _FilesystemBaseError(IOError):
	"""
	Base class for filesystem-related errors, a simple wrapper for the `IOError`.

	The only reasons why this class exists are:
		* it can build a new error from another `IOError` given as a 1st argument
		*
			it performs some automatic type conversion for input arguments
			(in case exception itself is constructed incorrectly)
		* it lets us catch more specific errors
		* it auto-generates the default error string if none is given
	"""
	def __init__(
		self,
		err_num,  # type: _t.Union[int, IOError]
		filename=None,  # type: _t.Union[None, str, _uni]
		err_str=None  # type: _t.Union[None, str, _uni]
	):
		if isinstance(err_num, IOError):
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
		if not isinstance(arg, (str, _uni)):
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
		super(NotExist, self).__init__(errno.ENOENT, filename, err_str)


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
		super(NotDir, self).__init__(errno.ENOTDIR, filename, err_str)


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
		super(NotFile, self).__init__(errno.EISDIR, filename, err_str)


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
		super(NotReadable, self).__init__(errno.EACCES, filename, err_str)


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
		super(NotWriteable, self).__init__(errno.EACCES, filename, err_str)


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
		super(UnknownObject, self).__init__(errno.ENOSYS, filename, err_str)


class _FileOverwriteBaseError(_FilesystemBaseError):
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
		super(_FileOverwriteBaseError, self).__init__(errno.EEXIST, filename, err_str)
		self.overwrite = overwrite


class FileAlreadyExist(_FileOverwriteBaseError):
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


class ParentFolderIsFile(_FileOverwriteBaseError):
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
