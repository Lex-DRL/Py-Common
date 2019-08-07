"""
Enum-style module specifying the modes supported by encoding detection for txt-file.

No external dependencies:
	*
		**BUILT_IN**: Detect only `ascii` or `utf-8` (with 1.0 precision) if possible,
		use the default system's codepage (with 0.0 precision) otherwise.

Depending on external modules,
the above "dummy" check (BOM/UTF-8/ASCII) is **NOT** performed:
	* **CHARDET**: use `chardet` module only.
	* **CHARDET_DAMMIT**: use `chardet` **WITH** `beautifulsoup4.UnicodeDammit`.

A combination of both previous approaches.
First, try to detect the encoding the "dummy" way (BOM/UTF-8/ASCII).
Then, if no success, use the modules specified above:
	* **FALLBACK_CHARDET**
	* **FALLBACK_CHARDET_DAMMIT**

"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

BUILT_IN = 0

CHARDET = 1
CHARDET_DAMMIT = 2

FALLBACK_CHARDET = 3
FALLBACK_CHARDET_DAMMIT = 4

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
