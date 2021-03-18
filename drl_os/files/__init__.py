"""
"""

__author__ = 'Lex Darlog (DRL)'
__all__ = (
	# packages:

	# modules:
	'error_check',
	'errors',
	'file_time',

	# classes:

	# functions:
	'to_windows_path', 'to_unix_path',  # from __convert_path

	# objects:
	'slash', 'slash_win',  # from __convert_path
)

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from .__convert_path import *
