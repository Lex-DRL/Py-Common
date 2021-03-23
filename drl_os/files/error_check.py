__author__ = 'Lex Darlog (DRL)'

from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
	path_t as _path_t,
	path_h as _path_h,
)
from . import errors as _err
from .__convert_path import to_unix_path as _to_unix
import os as _os
from os import path as _pth


def path_exists(
	path,  # type: _path_h
	not_link=False,
):
	path = _to_unix(path)
	if not _pth.exists(path):
		raise _err.NotExist(path)
	if not_link and _pth.islink(path):
		raise _err.PathAlreadyExist(path, err_str='Path already exists as link')
	return path


def dir_exists(
	path,  # type: _path_h
	not_link=False,
):
	path = path_exists(path, False)
	if not _pth.isdir(path):
		raise _err.NotDir(path)
	if not_link and _pth.islink(path):
		raise _err.PathAlreadyExist(path, err_str='Dir already exists as link')
	return path


def file_exists(
	path,  # type: _path_h
	not_link=False,
):
	path = path_exists(path, False)
	if not _pth.isfile(path):
		raise _err.NotFile(path)
	if not_link and _pth.islink(path):
		raise _err.FileAlreadyExist(path, err_str='File already exists as link')
	return path


def file_readable(
	path,  # type: _path_h
	not_link=False,
	try_read=False,
):
	path = file_exists(path, not_link)

	def _is_problem():
		if not _os.access(path, _os.R_OK):
			return True
		if try_read:
			try:
				first_bytes = min(8, _pth.getsize(path))  # int for now
				with open(path, 'rb') as fl:
					fl.read(first_bytes)  # str now
			except IOError:
				return True
		return False

	if _is_problem():
		raise _err.NotReadable(path)
	return path


def file_writeable(
	path,  # type: _path_h
	not_link=True,
):
	path = file_exists(path, not_link)
	if not _os.access(path, _os.W_OK):
		raise _err.NotWriteable(path)
	return path
