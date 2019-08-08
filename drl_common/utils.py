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
		kwargs  # type: _t.Dict[str, _t.Any]
	):
		"""
		Make sure all the given items (i.e., key-value pairs) have proper names.

		Throw an error if a key:
			* is empty or not a string at all
			* contains or starts from an unsupported character
			* clashes with a class' built-in members.
			* is passed multiple times
		"""
		seen = set()  # type: _t.Set[str]
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


class Enum(object):
	"""
	A modified version of ``Container`` class
	designed specifically as enum-style object which values has to be ints.

	=======
	Example
	=======

	::

		my_enum = Enum('MyEnum')
		my_enum.DEFAULT = 0
		my_enum.AAA = 1
		my_enum.BBB = 1

		my_enum._cache_members()  # you need to call it after all members defined

	"""

	# region Error-checkers for members being added

	@staticmethod
	def __check_errors(
		name,  # type: str
		value,  # type: int
		enum_nm,  # type: _t.Optional[_str_hint]
		seen_values_set,  # type: _t.Set[int]
		seen_values_set_add,  # type: _t.Callable[[int], None]
		seen_values_dict  # type: _t.Dict[int, str]
	):
		if not isinstance(value, int):
			raise TypeError(
				"Enum{} member {} should have int value. Got: {}".format(
					'({})'.format(repr(enum_nm)) if enum_nm else '',
					repr(name), repr(value)
				)
			)
		if value in seen_values_set:
			raise ValueError(
				"Enum{} can't have multiple members with the same value: {} -> {}".format(
					'({})'.format(repr(enum_nm)) if enum_nm else '',
					'({}, {})'.format(seen_values_dict[value], name),
					value
				)
			)
		seen_values_set_add(value)
		seen_values_dict[value] = name
		return value

	@staticmethod
	def __check_item(
		name,  # type: _str_t
		value,  # type: int
		enum_nm,  # type: _t.Optional[_str_hint]
		class_reserved_children,  # type: _t.Set[str]
		seen_keys_set,  # type: _t.Set[str]
		seen_keys_set_add,  # type: _t.Callable[[str], None]
		seen_values_set,  # type: _t.Set[int]
		seen_values_set_add,  # type: _t.Callable[[int], None]
		seen_values_dict  # type: _t.Dict[int, str]
	):
		name = _container_check_name(
			name, class_reserved_children, seen_keys_set, seen_keys_set_add
		)
		check_f = Enum.__check_errors
		return (
			name,
			check_f(
				name, value, enum_nm, seen_values_set, seen_values_set_add,
				seen_values_dict
			)
		)

	@staticmethod
	def __check_no_clash(
		name,  # type: _str_t
		value,  # type: int
		enum_nm,  # type: _t.Optional[_str_hint]
		class_reserved_children,  # type: _t.Set[str]
		seen_values_set,  # type: _t.Set[int]
		seen_values_set_add,  # type: _t.Callable[[int], None]
		seen_values_dict,  # type: _t.Dict[int, str]
		instance
	):
		name = _container_check_no_class_clash(
			name, class_reserved_children, instance
		)
		check_f = Enum.__check_errors
		return (
			name,
			check_f(
				name, value, enum_nm, seen_values_set, seen_values_set_add,
				seen_values_dict
			)
		)

	# endregion

	@classmethod
	def __class_children(cls):
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
		kwargs,  # type: _t.Dict[str, int]
		enum_nm=None  # type: _t.Optional[_str_hint]
	):
		"""
		Make sure all the given items (i.e., key-value pairs) have proper names.

		Throw an error if a key:
			* is empty or not a string at all
			* contains or starts from an unsupported character
			* clashes with a class' built-in members.
			* is passed multiple times
			* it's value already present as another enum member

		:param kwargs: the dict of member names and their internal enum-values.
		:param enum_nm: the name of Enum itself, used for meaningful errors.
		:return: a generator of checked items (name-value pairs).
		"""
		seen_keys = set()  # type: _t.Set[str]
		seen_keys_add = seen_keys.add
		seen_values = set()  # type: _t.Set[int]
		seen_values_add = seen_values.add
		seen_values_dict = dict()  # type: _t.Dict[int, str]
		class_children = cls.__class_children()
		internal_names = cls.__internal_names
		gen = (
			(k, v) for k, v in kwargs.iteritems()
			if k not in internal_names
		)
		check_f = cls.__check_item
		return (
			check_f(
				k, v, enum_nm, class_children,
				seen_keys, seen_keys_add,
				seen_values, seen_values_add, seen_values_dict
			) for k, v in gen
		)

	def __init__(
		self,
		name=None,  # type: _t.Optional[_str_hint]
		default=0,
		**children  # type: int
	):
		"""

		:param name: An optional name of the enum.
		:param default: A value of the enum member used as a default mode.
		:param children: enum members added right at the initialization.
		"""
		super(Enum, self).__init__()
		self.__dict__.update(
			dict(self.__class__.__proper_items(children, name))
		)
		if not(name is None or isinstance(name, _str_t)):
			name = repr(name)
		self.__enum_name = name
		self.__enum_default_val = default
		self.__enum_default_key = ''
		self.__enum_dict = dict()  # type: _t.Dict[str, int]
		self.__all_keys = set()  # type: _t.Set[str]
		self.__all_values = set()  # type: _t.Set[int]
		self.__key_mappings = dict()  # type: _t.Dict[int, str]
		self._cache_members()

	__internal_names = {
		'__doc__',
		'_Enum__doc__',

		'_Enum__enum_name',
		'_Enum__enum_default_val',
		'_Enum__enum_default_key',
		'_Enum__enum_dict',
		'_Enum__all_keys',
		'_Enum__all_values',
		'_Enum__key_mappings',
	}

	def _cache_members(self):
		"""
		After all the enum-members are added, error-check and cache them internally
		to make them appear in the built-in enum methods.

		This step is necessary for the performance reasons: it's much better
		to perform all the error-checks and cache all the members once,
		as the last stage of an enum setup, and work with them later using fast
		hash-sets, rather then perform these checks each time a member is accessed.
		"""
		items = sorted(self.__iteritems_no_cache())
		self.__enum_dict = dict(items)  # type: _t.Dict[str, int]
		self.__all_keys = {k for k, v in items}  # type: _t.Set[str]
		self.__all_values = {v for k, v in items}  # type: _t.Set[int]
		self.__key_mappings = {v: k for k, v in items}  # type: _t.Dict[int, str]
		if self.__all_values:
			# make sure the default value is actually in the set,
			# if we do have any members defined already
			if self.__enum_default_val not in self.__all_values:
				self.__enum_default_val = sorted(self.__all_values)[0]
			self.__enum_default_key = self.__key_mappings[self.__enum_default_val]

	def __iteritems_no_cache(self):
		"""
		An iterator over raw enum items. Unlike public methods, this one doesn't
		use any caches and iterate over members actually found on the enum instance.

		Should be used only internally to actually build those caches, since
		this method is much slower.
		"""
		class_children = self.__class__.__class_children()
		seen_v = set()  # type: _t.Set[int]
		seen_v_add = seen_v.add
		seen_v_dict = dict()  # type: _t.Dict[int, str]
		internal_names = self.__class__.__internal_names
		gen = (
			(k, v) for k, v in self.__dict__.iteritems()
			if k not in internal_names
		)
		enum_nm = self.__enum_name
		check_f = self.__check_no_clash
		return (
			check_f(
				k, v, enum_nm, class_children,
				seen_v, seen_v_add, seen_v_dict, self
			) for k, v in gen
		)

	def name(
		self,
		value  # type: int
	):
		"""
		Given the value of an enum-member, get it's name.

		If enum doesn't have a mamber with this value, no error is thrown,
		but the default member's name is returned.
		"""
		try:
			return self.__key_mappings[value]
		except KeyError:
			return self.__enum_default_key

	@property
	def all_names(self):
		"""A set containing **names** of all the enum's members."""
		return self.__all_keys

	@property
	def all_values(self):
		"""A set containing **values** of all the enum's members."""
		return self.__all_values

	def iteritems(self):
		"""A name-value iterator over all the enum members."""
		return self.__enum_dict.iteritems()

	def __repr__(self):
		enum_name = self.__enum_name
		return '<{enm}({nm})>'.format(
			enm=self.__class__.__name__,
			nm='' if (enum_name is None) else repr(enum_name),
		)

	def __getitem__(
		self,
		key  # type: str
	):
		try:
			return self.__enum_dict[key]
		except KeyError:
			return self.__enum_default_val

	# TODO
	# def __setattr__(self, key, value):
	# 	# perform check if not batch-assignment (with calling cache afterwards)
	# 	pass


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
