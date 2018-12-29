__author__ = 'DRL'



from . import errors
import os


def not_existing_path(path):
	from . import to_unix_path
	path = to_unix_path(path)
	if not os.path.exists(path):
		raise errors.NoFileOrDirError(path)
	return path


def not_existing_dir(path):
	path = not_existing_path(path)
	if not os.path.isdir(path):
		raise errors.NotDirError(path)
	return path


def not_existing_file(path):
	path = not_existing_path(path)
	if not os.path.isfile(path):
		raise errors.NotFileError(path)
	return path


def path_not_readable(path):
	path = not_existing_file(path)
	if not os.access(path, os.R_OK):
		raise errors.NotReadable(path)
	return path


def path_not_writeable(path):
	path = not_existing_file(path)
	if not os.access(path, os.W_OK):
		raise errors.NotWriteable(path)
	return path
