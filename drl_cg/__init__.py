"""
A big package group containing all the modules related to CG-soft (2D/3D).
"""

__author__ = 'Lex Darlog (DRL)'
__all__ = (
	# sub-packages:
	'houdini',
	'nuke',
	'unity',

	# modules:
	'launcher'

	# objects:
)

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_h
)

# endregion

