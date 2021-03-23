__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	path_t as _path_t,
	path_h as _path_h,
)


slash = '/'
slash_win = "q\\q"[1]  # fix for houdini: for some reason it errors on '\\'


def __convert_path_slashes(
	path,
	wrong_slash=slash_win, right_slash=slash,
	trailing_slash=None, leading_slash=0
):
	assert isinstance(path, _path_t), "Not a valid path"
	if not path:
		return ''

	path = path.replace(wrong_slash, right_slash)
	if not (trailing_slash is None):
		path = path.rstrip(right_slash)
		if trailing_slash:
			path += right_slash
	if not (leading_slash is None):
		path = path.lstrip(right_slash)
		if leading_slash:
			path = right_slash + path
	return path


def to_windows_path(
	path,  # type: _path_h
	trailing_slash=None,  # type: _t.Optional[bool]
	leading_slash=False  # type: _t.Optional[bool]
):
	"""
	Ensures given path has Windows-style slashes. ("/" -> "\")

	:param path: The path.
	:param trailing_slash:
		Whether we need to ensure path has or lacks trailing slash:
			*
				``None``: (default) no check performed.
				Leave as is, just replace path slashes.
			* ``False``: Force-remove trailing slash
			* ``True``: Force-leave (single) trailing slash.
	:param leading_slash:
		The same for leading slash.
		However, it's `False` (force-removed) by default.
	"""
	return __convert_path_slashes(
		path, slash, slash_win, trailing_slash, leading_slash
	)


def to_unix_path(
	path,  # type: _path_h
	trailing_slash=None,  # type: _t.Optional[bool]
	leading_slash=False  # type: _t.Optional[bool]
):
	"""
	Ensures given path has unix-style slashes. ("\" -> "/")

	:param path: The path.
	:param trailing_slash:
		Whether we need to ensure path has or lacks trailing slash:
			*
				``None``: (default) no check performed.
				Leave as is, just replace path slashes.
			* ``False``: Force-remove trailing slash
			* ``True``: Force-leave (single) trailing slash.
	:param leading_slash:
		The same for leading slash.
		However, it's `False` (force-removed) by default.
	"""
	return __convert_path_slashes(
		path,
		trailing_slash=trailing_slash, leading_slash=leading_slash
	)
