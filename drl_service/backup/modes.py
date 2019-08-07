"""
Enum-style module, defining supported backup methods.
	* `REPLACE` - remove existing files/folders at the out path before backing up.
	* `SUBDIR_DATE` - create a sub-folder with the backup date.
	* `SUBDIR_VER` - create a sub-folder with an incrementing version number.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

REPLACE = 1
SUBDIR_DATE = 2
SUBDIR_VER = 3


all_modes = {
	_k: _v for _k, _v in locals().items()
	if not (
		_k.startswith('_') or
		_k in {'all_modes', }
	)
}  # type: _t.Dict[str, int]


__mode_key_mappings = {
	_v: _k for _k, _v in all_modes.iteritems()
}  # type: _t.Dict[int, str]


def mode_key(
	mode_value  # type: int
):
	"""
	Get the human-readable name of given mode.
	"""
	try:
		return __mode_key_mappings[mode_value]
	except KeyError:
		return None
