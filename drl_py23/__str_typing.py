"""Python-version-independent type hints for various string types."""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as __t
except ImportError:
	pass

try:
	# noinspection PyUnresolvedReferences,PyCompatibility
	from pathlib import (
		Path as __Path,
		PurePath as __PurePath,
	)
except ImportError:
	pass


# noinspection PyBroadException,PyPep8
try:
	t_strict_str = str
	t_strict_unicode = unicode
except:
	t_strict_str = bytes
	t_strict_unicode = str

# -----------------------------------------------------------------------------

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	str_t = (str, unicode)
except:
	str_t = (str, bytes)

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	str_h = __t.Union[str, unicode]
except:
	# noinspection PyBroadException,PyPep8
	try:
		# noinspection PyUnresolvedReferences
		str_h = __t.Union[str, bytes]
	except:
		str_h = str

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	str_h_o = __t.Optional[str_h]
except:
	str_h_o = str_h

# -----------------------------------------------------------------------------

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	path_t = (t_strict_str, t_strict_unicode, __Path, __PurePath)
except:
	path_t = str_t

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	path_h = __t.Union[str_h, __Path, __PurePath]
except:
	path_h = str_h

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	path_h_o = __t.Optional[path_h]
except:
	path_h_o = path_h

# -----------------------------------------------------------------------------

# legacy backwards compatibility:
str_hint = str_h
