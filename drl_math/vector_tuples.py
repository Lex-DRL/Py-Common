"""
This module provides named-tuple classes for vectors.
They're useful instead of app-specific ones for:
	* simplicity of a named tuple.
	* type-hints.
	* ability to store ints/strings.
"""

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from collections import namedtuple as _namedtuple

Vector4 = _namedtuple('Vector4', ['x', 'y', 'z', 'w'])
Vector3 = _namedtuple('Vector4', ['x', 'y', 'z'])
Vector2 = _namedtuple('Vector4', ['x', 'y'])

# -----------------------------------------------------------------------------

try:
	FloatVector4 = _t.NamedTuple('FloatVector4', [('x', float), ('y', float), ('z', float), ('w', float)])
except:
	FloatVector4 = _namedtuple('FloatVector4', ['x', 'y', 'z', 'w'])

try:
	FloatVector3 = _t.NamedTuple('FloatVector3', [('x', float), ('y', float), ('z', float)])
except:
	FloatVector3 = _namedtuple('FloatVector3', ['x', 'y', 'z'])

try:
	FloatVector2 = _t.NamedTuple('FloatVector2', [('x', float), ('y', float)])
except:
	FloatVector2 = _namedtuple('FloatVector2', ['x', 'y'])

# -----------------------------------------------------------------------------

try:
	IntVector4 = _t.NamedTuple('IntVector4', [('x', int), ('y', int), ('z', int), ('w', int)])
except:
	IntVector4 = _namedtuple('IntVector4', ['x', 'y', 'z', 'w'])

try:
	IntVector3 = _t.NamedTuple('IntVector3', [('x', int), ('y', int), ('z', int)])
except:
	IntVector3 = _namedtuple('IntVector3', ['x', 'y', 'z'])

try:
	IntVector2 = _t.NamedTuple('IntVector2', [('x', int), ('y', int)])
except:
	IntVector2 = _namedtuple('IntVector2', ['x', 'y'])

# -----------------------------------------------------------------------------

try:
	StrVector4 = _t.NamedTuple('StrVector4', [('x', str), ('y', str), ('z', str), ('w', str)])
except:
	StrVector4 = _namedtuple('StrVector4', ['x', 'y', 'z', 'w'])

try:
	StrVector3 = _t.NamedTuple('StrVector3', [('x', str), ('y', str), ('z', str)])
except:
	StrVector3 = _namedtuple('StrVector3', ['x', 'y', 'z'])

try:
	StrVector2 = _t.NamedTuple('StrVector2', [('x', str), ('y', str)])
except:
	StrVector2 = _namedtuple('StrVector2', ['x', 'y'])
