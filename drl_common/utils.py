__author__ = 'DRL'

import string as _string
from collections import Iterable as _Iterable
from . import errors as err

try:
	_str_t = (str, unicode)
except:
	_str_t = (str, )

try:
	# support type hints:
	import typing as _t
except ImportError:
	pass


class Container(object):
	"""
	Just a dummy service class, acting like
	an editable namedtuple.

	It's child elements can be added:
		* on object creation (as arguments):
			``Container(a=1, b=[])``
		* simply by assignment with a dot operator:
			``q = Container();``
			``q.a = 1;``
			``q.b = []``

	Both ways are equally good, and all the children
	added after creation are also tracked and returned by
	respective methods.
	"""

	@classmethod
	def _class_children(cls):
		"""
		The method returning a set of fields/methods defined in the class itself.
		It's used to prevent users from overriding those children with their own
		items of the same name.
		"""
		res = {nm for nm in dir(cls) if not nm.startswith('_')}  # type: _t.Set[str]
		return res

	@classmethod
	def __proper_items(cls, **kwargs):
		"""
		Filter out any items (i.e., key-value pairs) which keys are somehow unsupported.
		I.e., with a key that:
			* is empty or not a string at all
			* starts with an unsupported character ('_' or not ascii)
			* clashes with a class' built-in members.

		The resulting items are always sorted by key.
		Duplicated keys are removed but it's unclear which value is kept
		since `kwargs` dict is unordered.
		"""
		seen = set()
		seen_add = seen.add
		class_children = cls._class_children()
		return sorted(
			(k, v) for k, v in
			kwargs.iteritems()
			if (
				k
				and isinstance(k, _str_t)
				and k[0] in _string.ascii_letters
				# and not k.startswith('_')  # already covered by previous ^ condition
				and k not in class_children
				and not(k in seen or seen_add(k))  # ensure each key is unique and add if it is
			)
		)

	def __init__(self, **kwargs):
		super(Container, self).__init__()
		self.__dict__.update(
			dict(self.__class__.__proper_items(**kwargs))
		)

	def items(self):
		"""
		List of key-value tuple pairs of children.
		"""
		return self.__class__.__proper_items(**self.__dict__)

	def as_dict(self):
		"""
		A dictionary of children. You're safe to edit it.
		"""
		return dict(self.items())

	def update(self, **kwargs):
		self.__dict__.update(
			dict(self.__class__.__proper_items(**kwargs))
		)

	def __repr__(self):
		res_values = self.items()
		num = len(res_values)
		pre, separator, post = '', ', ', ''
		if (
			num > 3 or (
				num > 0 and any(
					(isinstance(val, _Iterable) and not isinstance(val, _str_t))
					for nm, val in (res_values if num < 4 else res_values[:3])
				)
			)
		):
			pre, separator, post = '\n\t', ',\n\t', '\n'

		res_values = [
			'{0}={1}'.format(nm, repr(val))
			for nm, val in res_values
		]
		res_values = separator.join(res_values)
		if res_values:
			res_values = pre + res_values + post
		return '{0}({1})'.format(self.__class__.__name__, res_values)


Dummy = Container  # fallback for a legacy code


def remove_duplicates(items=None):
	"""
	Removes duplicate entities in the list or tuple. Keeps the order.

	:param items: list or tuple
	:return: depending on the input, either list or tuple, in which each element is unique.
	"""
	err.WrongTypeError(items, (list, tuple), 'items').raise_if_needed()
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
	err.WrongTypeError(
		subtracted_list, (list, tuple), 'subtracted_list'
	).raise_if_needed()
	err.WrongTypeError(source_list, (list, tuple), 'source_list').raise_if_needed()
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



def camel_case(string='', punctuation_to_underscores=True, small_first_letter=True):
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
			# How much the current value is offset from it's index.
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
		key_f = lambda x: repr(x)

	grouped = dict()  # start as dict, for easier grouping
	grouped_setdefault = grouped.setdefault
	get_group = lambda key: grouped_setdefault(key, [])  # init new list, if necessary
	for i in items:
		get_group(key_f(i)).append(i)

	return [  # list of tuples:
		tuple(v) for k, v in sorted(
			grouped.iteritems(),
			key=lambda x: x[0]
		)
	]
