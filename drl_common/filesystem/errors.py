__author__ = 'DRL'

import errno


class FilesystemBaseError(IOError):
	"""
	Base class for filesystem-related errors.

	The only two reasons why this class exists are:

	* it performs some automatic type conversion for input arguments (in case exception itself is constructed incorrectly)
	* it allows me to catch any of my own errors.

	:param message: <str> The required error description. I.e.: 'File already exist'.
	:param filename: <str> Optional path to file.
	:param err_num: Error number (from standard <errno> module).
	"""
	def __init__(self, message, filename=None, err_num=errno.EPERM):
		if not (err_num and isinstance(err_num, int)):
			err_num = errno.EPERM
		if not isinstance(message, (str, unicode)):
			try:
				message = str(message)
			except:
				message = unicode(message)
		if filename is None:
			super(FilesystemBaseError, self).__init__(err_num, message)
			return
		if not isinstance(filename, (str, unicode)):
			try:
				filename = str(filename)
			except:
				filename = unicode(filename)
		super(FilesystemBaseError, self).__init__(err_num, message, filename)


class NoFileOrDirError(FilesystemBaseError):
	"""
	Given path doesn't exist.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='No such file or directory'):
		super(NoFileOrDirError, self).__init__(message, filename, errno.ENOENT)


class EmptyPathError(NoFileOrDirError):
	"""
	Empty path provided.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Empty path provided'):
		super(EmptyPathError, self).__init__(message, filename)


class NotDirError(FilesystemBaseError):
	"""
	Given path is not a folder.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Not a directory'):
		super(NotDirError, self).__init__(message, filename, errno.ENOTDIR)


class NotFileError(FilesystemBaseError):
	"""
	Given path is not a file.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Not a file'):
		super(NotFileError, self).__init__(message, filename, errno.EISDIR)


class NotReadable(FilesystemBaseError):
	"""
	Given file/folder is not readable.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Not readable'):
		super(NotReadable, self).__init__(message, filename, errno.EACCES)


class NotWriteable(FilesystemBaseError):
	"""
	Given file/folder is not readable.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Not writeable'):
		super(NotWriteable, self).__init__(message, filename, errno.EACCES)


class UnknownObjectError(FilesystemBaseError):
	"""
	Given path doesn't exist.

	:param filename: <str> Optional path to the file.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, message='Unknown filesystem object'):
		super(UnknownObjectError, self).__init__(message, filename, errno.ENOSYS)


class FileOverwriteBaseError(FilesystemBaseError):
	"""
	Unsuccessful attempt to overwrite a file/folder.

	In other words, you're trying to create folder/file that already exist at the given path.

	:param filename: <str> Optional path to the file.
	:param overwrite: <int/bool/None> Whether you tried to overwrite the file first. I.e.:
	* None: it's unknown if this error happened because you just disabled overwrite or because it just can't be overwritten.
	* 0/False: You're trying to add a folder/file at the path that already exist, and you didn't try to overwrite it.
	* 1/True: You tried to overwrite the path first, but you can't do that for unknown reason.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, overwrite=None, message='File already exist'):
		if not (overwrite is None):
			message += ' (overwrite=<%s>)' % overwrite
		super(FileOverwriteBaseError, self).__init__(message, filename, errno.EEXIST)
		self.overwrite = overwrite


class FileAlreadyExistError(FileOverwriteBaseError):
	"""
	An attempt to create/write a file that already exist.

	:param filename: <str> Optional path to the file.
	:param overwrite: <int/bool/None> Whether you tried to overwrite the file first. I.e.:
	* None: it's unknown if this error happened because you just disabled overwrite or because it just can't be overwritten.
	* 0/False: You're trying to add a file at the path that already exist, and you didn't try to overwrite it.
	* 1/True: You tried to overwrite the path first, but you can't do that for unknown reason.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, overwrite=None, message='File already exist'):
		super(FileAlreadyExistError, self).__init__(filename, overwrite, message)


class ParentFolderIsFileError(FileOverwriteBaseError):
	"""
	An attempt to call a file while one of it's breadcrumb folders is a file itself.

	:param filename: <str> Optional path to the file.
	:param parent_folder: <str> Optional path to a folder which turned out to be a file.
	:param overwrite: <int/bool/None> Whether you tried to overwrite the file first. I.e.:
	* None: it's unknown if this error happened because you just disabled overwrite or because it just can't be overwritten.
	* 0/False: You didn't try to replace the "parent file" with the folder.
	* 1/True: You tried to overwrite the path first, but you can't do that for unknown reason.
	:param message: <str> The main error message. You may modify it, but it's a required string argument.
	"""
	def __init__(self, filename=None, parent_folder=None, overwrite=None, message='Parent folder is file'):
		if not (parent_folder is None):
			if not isinstance(parent_folder, (str, unicode)):
				try:
					parent_folder = str(parent_folder)
				except:
					parent_folder = unicode(parent_folder)
			message += ' (folder: "%s")' % parent_folder
		super(ParentFolderIsFileError, self).__init__(filename, overwrite, message)
		self.parent_folder = parent_folder
