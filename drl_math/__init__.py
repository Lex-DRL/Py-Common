"""
Common math classes not implemented in standard python libs which are too simple
to use monstrous packages like `numpy` just for them.
"""

__author__ = 'Lex Darlog (DRL)'
__all__ = (
	# submodules:
	'vector_tuples',

	# classes:
	'GeometricProgression'
)

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
	_t_num = _t.Union[int, float]
except ImportError:
	pass

from drl_common.cols import Dummy as _Dummy
from drl_common.py_2_3 import (
	xrange as _xrange,
)


class GeometricProgression(object):
	def __init__(
		self,
		n,  # type: int
		ratio,  # type: _t_num
		start=1.0,
		nocache=False,
	):
		"""
		A class providing common geometric progression operations.

		:param n: number of elements.
		:param ratio: multiplier.
		:param start: first element.
		:param nocache:
			If `True`, the sequence is not cached internally and is re-calculated
			on each call.
			Useful to reduce memory footprint for very long progressions, which should
			use a generator instead of in-memory sequence anyway.
		"""
		super(GeometricProgression, self).__init__()
		self.__n = max(n, 1)
		self.__ratio = ratio
		self.__start = start
		self.__seq_is_cached = False
		self.__seq = tuple()  # type: _t.Tuple[_t_num]
		self.__nocache = nocache

	def __reset_cache(self):
		self.__seq_is_cached = False
		self.__seq = tuple()  # type: _t.Tuple[_t_num]

	@property
	def n(self):
		return self.__n

	@n.setter
	def n(self, value):
		value = max(value, 1)
		if value == self.__n:
			return
		self.__n = value
		self.__reset_cache()

	@property
	def ratio(self):
		return self.__ratio

	@ratio.setter
	def ratio(self, value):
		if value == self.__ratio:
			return
		self.__ratio = value
		self.__reset_cache()

	@property
	def start(self):
		return self.__start

	@start.setter
	def start(self, value):
		if value == self.__start:
			return
		self.__start = value
		self.__reset_cache()

	@property
	def nocache(self):
		return self.__nocache

	@nocache.setter
	def nocache(self, value):
		if value == self.__nocache:
			return
		self.__nocache = value
		self.__reset_cache()

	def sequence_gen(self):
		"""Generator for the sequence."""
		n, first, ratio = self.n, self.start, self.ratio
		if first == 0:
			return (0 for i in _xrange(n))

		buf = _Dummy()
		# The buffer actually stores the next value, so it's one step in advance.
		# But this single last extra-calculation is negligible by performance.
		buf.next_val = first  # type: _t_num

		def next_item():
			cur = buf.next_val
			buf.next_val *= ratio
			return cur

		# made via generator expression - since it leads to more efficient
		# list/tuple initialisation due to automatic detection of items count:
		return (next_item() for i in _xrange(n))

	@property
	def sequence(self):
		"""The progression's sequence as tuple."""
		if self.__seq_is_cached:
			return self.__seq
		seq = tuple(self.sequence_gen())
		if self.__nocache:
			return seq
		self.__seq = seq
		self.__seq_is_cached = True
		return seq

	def sum(self):
		"""Sum of all `n` elements of the progression."""
		n, first, ratio = self.n, self.start, self.ratio
		# https://en.wikipedia.org/wiki/Geometric_progression
		if first == 0 or ratio == 0:
			return 0
		if ratio == 1:
			return first * n
		return first * (1 - ratio ** n) / (1 - ratio)

	def __repr__(self):
		return '{}({}, ratio={}, first={})'.format(
			self.__class__.__name__, self.__n, self.__ratio, self.__start
		)
