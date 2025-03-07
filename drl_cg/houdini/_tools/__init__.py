"""
Scripts that are supposed to be launched directly by an end user, as a
complete command-line programs doing something with Houdini.
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

