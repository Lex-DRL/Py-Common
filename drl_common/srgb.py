__author__ = 'Lex Darlog (DRL)'

from . import errors as _err

# conversion matrices for CIE XYZ space:
# from pymel.core.datatypes import Vector, Matrix
#
# _mtx_to_sr# gb = Matrix(
# 	[3.2406, -1.5372, -0.4986],
# 	[-0.9689, 1.8758, 0.0415],
# 	[0.0557, -0.2040, 1.0570]
# )
# _mtx_from_srgb = Matrix(
# 	[0.4124, 0.3576, 0.1805],
# 	[0.2126, 0.7152, 0.0722],
# 	[0.0193, 0.1192, 0.9505]
# )
_a = 0.055
_a_one = 1.055
_a_one_inv = 1.0 / _a_one
_c_mul = 12.92
_c_mul_inv = 1.0 / _c_mul
_pow = 2.4
_pow_inv = 1.0 / _pow


def linear_to_srgb(*color):
	"""
	Convert color value from Linear space to sRGB.

	:param color:
		linear color:
		either single iterable arg or a sequence of scalar args.
	:type color: int|float
	"""
	def calc_comp(c):
		if c <= 0.0031308:
			return c * _c_mul
		# return (1 + _a) * pow(c, 1.0 / 2.4) - _a
		return _a_one * pow(c, _pow_inv) - _a

	lc = len(color)
	_err.NoValueError('color').raise_by_condition(lc, lambda x: x < 1)
	clr = color[0] if (lc == 1) else color
	if isinstance(clr, (int, float)):
		clr = [clr]
	return map(calc_comp, clr)


def srgb_to_linear(*color):
	"""
	Convert color value from sRGB space to Linear.

	:param color:
		sRGB color:
		either single iterable arg or a sequence of scalar args.
	:type color: int|float
	"""
	def calc_comp(c):
		if c <= 0.04045:
			return c * _c_mul_inv
		# return pow((c + _a) / (1 + _a), _pow)
		return pow((c + _a) * _a_one_inv, _pow)

	lc = len(color)
	_err.NoValueError('color').raise_by_condition(lc, lambda x: x < 1)
	clr = color[0] if (lc == 1) else color
	if isinstance(clr, (int, float)):
		clr = [clr]
	return map(calc_comp, clr)
