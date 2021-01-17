__author__ = 'DRL'

from collections import (
	Iterable as _Iterable,
	Iterator as _Iterator
)
from .py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)
from . import errors as _err

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

try:
	from itertools import (
		izip as _izip,
		izip_longest as _izip_longest
	)
except ImportError:
	from itertools import zip_longest as _izip_longest
	_izip = zip

# only for backward compatibility in legacy code:
from .cols import DefaultTuple, DefaultList, Container
Dummy = Container


def remove_duplicates(items=None):
	"""
	Removes duplicate entities in the list or tuple. Keeps the order.

	:param items: list or tuple
	:return: depending on the input, either list or tuple, in which each element is unique.
	"""
	_err.WrongTypeError(items, (list, tuple), 'items').raise_if_needed()
	seen = set()
	seen_add = seen.add
	res = [
		x for x in items
		if not (x in seen or seen_add(x))
	]
	if isinstance(items, tuple):
		return tuple(res)
	return res


def list_difference(source_list, subtracted_list):
	"""
	Removes all occurrences of 2nd list elements from the 1st list.

	:param source_list: list or tuple
	:param subtracted_list: list or tuple
	:return: list or tuple
	"""
	_err.WrongTypeError(
		subtracted_list, (list, tuple), 'subtracted_list'
	).raise_if_needed()
	_err.WrongTypeError(source_list, (list, tuple), 'source_list').raise_if_needed()
	res = source_list[:]
	if not isinstance(res, list):
		res = list(res)
	rem = res.remove
	for s in subtracted_list:
		while s in res:
			rem(s)
	if isinstance(source_list, tuple):
		res = tuple(res)
	return res


def camel_case(
	string='', punctuation_to_underscores=True, small_first_letter=True
):
	import re
	# string='Some of my text is AWESOME, the other is not -_ all of it is cool'
	if not (isinstance(string, str) and string):
		return ''
	res = string.title()
	res = re.sub(r'\s', '', res)
	if punctuation_to_underscores:
		res = re.sub(r'\W+', '_', res)
		res = re.sub(r'__+', '_', res)
	else:
		res = re.sub(r'\W+', '', res)
		res = re.sub(r'_+', '', res)
	if small_first_letter and res:
		res = res[:1].lower() + res[1:]
	return res


def to_ranges_generator(iterable):
	"""
	Converts an iterable to a list of ranges.
	The function works only on pre-sorted iterables of ints
	(floats processed as ints, too).


	I.e.:
		list(to_ranges_generator([2, 3, 4, 5, 7, 8, 9, 11, -1, 0, 1]))

		# Result: [(2, 5), (7, 9), (11, 11), (-1, 1)]

	DRL: I have no idea how it works

	from: http://stackoverflow.com/questions/4628333/converting-a-list-of-integers-into-range-in-python

	:param iterable: A sequence of ints
	:return: <generator object>
	"""
	import itertools
	for key, range_group in itertools.groupby(
		enumerate(iterable),  # pairs of item's id in the list and it's actual value
		lambda (itm_id, val): val - itm_id
		# ^ How much the current value is offset from it's index.
		# Each range will have the same offset, so they'll end up in the same group.
	):
		range_group = list(range_group)
		yield (
			int(range_group[0][1]),  # range start value
			int(range_group[-1][1])  # range end value
		)


def to_ranges(iterable, to_tuple=True):
	"""
	Converts an iterable to a list of ranges.
	The function works only on pre-sorted iterables of ints
	(floats processed as ints, too).

	:param iterable: A sequence of ints
	:param to_tuple:
		<bool>
			* If True, the result is tuple tuples.
			* Otherwise, list of tuples.
	:return: <list/tuple of tuples> ranges
	"""
	gen = to_ranges_generator(iterable)
	out_type = tuple if to_tuple else list
	return out_type(gen)


# noinspection PyIncorrectDocstring
def group_items(items, key_f=None):
	"""
	Turns a plain iterable of items to a groups of items (list of tuples).
	Item's group is determined by the group_key_f function.

	:param key_f:
		<callable>

		It takes exactly one argument (the item)
		and returns whatever is considered a grouping/sorting key. (string, int, tuple...)

	:return:
		<list of tuples>

		* List contains groups.
		* Groups contain the actual items.
	"""
	if key_f is None or not callable(key_f):
		key_f = repr

	grouped = dict()  # start as dict, for easier grouping
	grouped_setdefault = grouped.setdefault

	def get_group(key):
		# init new list, if necessary:
		return grouped_setdefault(key, [])

	for i in items:
		get_group(key_f(i)).append(i)

	return [  # list of tuples:
		tuple(v) for k, v in sorted(
			grouped.iteritems(),
			key=lambda x: x[0]
		)
	]


# noinspection PyIncorrectDocstring
def flatten_gen(possibly_iterable, bruteforce=True, keep_strings=True):
	"""
	Generator turning any input to a flat sequence.
	the generator is recursive, so it can handle (almost)
	any depth of inner sequences.
	Strings are kept as a whole, not split to individual chars.

	I.e.:
		* 4 -> (4,)
		* [4, 5] -> (4, 5)
		* [4, (5, 6), 7, (['aaa'], [8], [{9}, 10])] -> (4, 5, 6, 7, 'aaa', 8, 9, 10)

	:param bruteforce:
		* **True**: Detect nested iterables by actually attempting to iterate over them.
		*
			**False**: Only classes that strictly comply to the pythonic definition
			of iterables are considered those. For example, a class can have
			`__getitem__()` and `__len__()` methods defined, but it's still **NOT**
			considered iterable because it doesn't have an `__iter__()` method.

		You may want to disable bruteforce to intentionally avoid going inside those
		"partially-compliant" iterables, but most of the time enabling it
		gives the most predictable result: anything that CAN be iterated - WILL be iterated.
	:param keep_strings:
		* **True**: nested strings are kept intact.
		*
			**False**: string-like types are treated as iterables and therefore
			are split into individual characters.
	"""
	if keep_strings and isinstance(possibly_iterable, _str_t):
		# string
		yield possibly_iterable
		return

	if bruteforce:
		# we try to detect non-iterable by actually attempting to iterate over it:
		try:
			possibly_iterable = iter(possibly_iterable)
		except TypeError:
			yield possibly_iterable
			return
	else:
		# only those classes inherited from built-in iterable classes
		# are considered iterables:
		if not isinstance(possibly_iterable, (_Iterable, _Iterator)):
			yield possibly_iterable
			return

	# it is indeed an iterable:
	for el in possibly_iterable:
		for sub in flatten_gen(el):
			yield sub


def group_by_n_gen(
	iterable, n, do_fill=True, fillvalue=None
):  # type: (_t.Iterable[T1], int, bool, T2) -> _t.Iterator[tuple[_t.Union[T1, T2], ...]]
	"""
	Group items in the iterable by n in each tuple.
	I.e.:

	range(9), n=3 -> [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
	"""
	assert (isinstance(n, int) and n > 0), "Wrong number of grouped items: {}".format(n)
	args = [iter(iterable)] * n
	if do_fill:
		return _izip_longest(*args, fillvalue=fillvalue)
	return _izip(*args)
