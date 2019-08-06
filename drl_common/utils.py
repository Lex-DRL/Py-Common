__author__ = 'DRL'

import string as _string
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

# allowed chars for the 1st char of a variable name:
_var_name_start_chars = set(_string.ascii_letters + '_')
# all allowed chars for a variable name:
_var_name_chars = set(_string.ascii_letters + '_' + _string.digits)


class DefaultTuple(tuple):
	"""
	Similar to DefaultDict, but a tuple.

	When accessing an index that currently is out of tuple's range,
	a default value is returned.
	"""
	def __init__(self, default='', *args, **kwargs):
		super(DefaultTuple, self).__init__(*args, **kwargs)
		self.default = default

	def __getitem__(self, item):
		try:
			return super(DefaultTuple, self).__getitem__(item)
		except IndexError:
			return self.default

	def __repr__(self):
		return '{cls}(default={d}, {val})'.format(
			cls=self.__class__.__name__,
			d=repr(self.default),
			val=super(DefaultTuple, self).__repr__()
		)


class DefaultList(list):
	"""
	Similar to DefaultDict, but a list.

	When accessing an index that currently is out of list's range,
	the list kept intact but a default value is returned.
	"""
	def __init__(self, default='', *args, **kwargs):
		super(DefaultList, self).__init__(*args, **kwargs)
		self.default = default

	def __getitem__(self, item):
		try:
			return super(DefaultList, self).__getitem__(item)
		except IndexError:
			return self.default

	def __repr__(self):
		return '{cls}(default={d}, {val})'.format(
			cls=self.__class__.__name__,
			d=repr(self.default),
			val=super(DefaultList, self).__repr__()
		)


def _container_proper_name(
	name,  # type: _str_t
	class_reserved_children,  # type: _t.Set[_str_t]
	seen_set,  # type: _t.Set[_str_t]
	seen_set_add,  # type: _t.Callable[[str], None]
):
	"""
	Whether the given name can be used as a container's member name.

	:param name: The name to check
	:param class_reserved_children:
		A string set containing names reserved for the class members.
	:param seen_set:
		A set used to verify if the same name was used multiple times
		during a single operation.
	:param seen_set_add:
		The set's add() method. Passed simply for performance reasons.
	:return:
		* ``True`` - if the name is OK.
		* ``False`` - if not.
	"""
	return (
		name
		and isinstance(name, _str_t)
		and name[0] in _var_name_start_chars
		and all(c in _var_name_chars for c in name[1:])
		# and not k.startswith('_')  # already covered by previous ^ condition
		and name not in class_reserved_children
		# ensure each key is unique and add it if it is:
		and not (name in seen_set or seen_set_add(name))
	)


def _container_check_name(
	name,  # type: _str_t
	class_reserved_children,  # type: _t.Set[str]
	seen_set,  # type: _t.Set[str]
	seen_set_add,  # type: _t.Callable[[str], None]
):
	"""
	Verify that the given name can be used as a container's member.
	Raise an error if anything is wrong.

	:param name: The name to check
	:param class_reserved_children:
		A string set containing names reserved for the class members.
	:param seen_set:
		A set used to verify if the same name was used multiple times
		during a single operation.
	:param seen_set_add:
		The set's add() method. Passed simply for performance reasons.
	:return: The passed name forcefully turned to a string.
	"""
	if not isinstance(name, _str_t):
		raise TypeError(
			"This can't be the name of the container's child: {}".format(repr(name))
		)
	if not name:
		raise ValueError("The container's child can't have an empty name.")

	if name[0] not in _var_name_start_chars:
		raise ValueError(
			"This can't be the name of the container's child "
			"since it starts from an unsupported character: {}".format(name)
		)
	if not all(
		c in _var_name_chars for c in name[1:]
	):
		raise ValueError(
			"This can't be the name of the class member "
			"since it contains an unsupported character: {}".format(name)
		)
	if not isinstance(name, str):
		name = str(name)

	if name in class_reserved_children:
		raise ValueError(
			"This name can't be used as the container's child "
			"since the container object already has a class method "
			"with the same name: {}".format(name)
		)
	if name in seen_set:
		raise ValueError(
			"Attempt to add the same container's child "
			"multiple times at once: {}".format(name)
		)
	seen_set_add(name)

	return name


def _container_check_no_class_clash(
	name,  # type: _str_t
	class_reserved_children,  # type: _t.Set[str]
	instance
):
	if not (name and isinstance(name, str)):
		raise ValueError(
			"The container's child can't have this name: {}".format(repr(name))
		)
	if name in class_reserved_children:
		raise ValueError(
			"The name of a container's class member \"{}\" is overridden "
			"on the instance: {}".format(name, instance)
		)
	return name


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
		res = set(dir(cls))  # type: _t.Set[str]
		return res

	@classmethod
	def __proper_items(
		cls,
		kwargs  # type: _t.Dict
	):
		"""
		Make sure all the given items (i.e., key-value pairs) have proper names.

		Throw an error if a key:
			* is empty or not a string at all
			* contains or starts from an unsupported character
			* clashes with a class' built-in members.
			* is passed multiple times
		"""
		seen = set()
		seen_add = seen.add
		class_children = cls._class_children()
		return (
			(
				_container_check_name(k, class_children, seen, seen_add),
				v
			) for k, v in kwargs.iteritems()
		)

	def __init__(self, **children):
		super(Container, self).__init__()
		self.__dict__.update(
			dict(self.__class__.__proper_items(children))
		)

	def iteritems(self):
		class_children = self.__class__._class_children()
		return (
			(_container_check_no_class_clash(k, class_children, self), v)
			for k, v in self.__dict__.iteritems()
		)

	def items(self):
		"""
		List of key-value tuple pairs of children.
		"""
		return sorted(self.iteritems())

	def as_dict(self):
		"""
		A dictionary of children. You're safe to edit it.
		"""
		return dict(self.iteritems())

	def update(self, **children):
		self.__dict__.update(
			dict(self.__class__.__proper_items(children))
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
