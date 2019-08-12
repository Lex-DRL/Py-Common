"""
A module containing various advanced collections designed to be used as
wrappers of some sort.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass
import types as _ts
from .py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)

from collections import (
	OrderedDict as _OrderedDict,
	Iterable as _Iterable,
	Iterator as _Iterator
)
import string as __string

# noinspection PyBroadException
try:
	_h_batch = _t.Dict[str, _t.Any]
	_h_batches = _t.Optional[_t.List[_h_batch]]
except:
	pass

# allowed chars for the 1st char of a variable name:
_var_name_start_chars = set(__string.ascii_letters + '_')
# all allowed chars for a variable name:
_var_name_chars = set(__string.ascii_letters + '_' + __string.digits)


class DefaultTuple(tuple):
	"""
	Similar to ``DefaultDict``, but a ``tuple``.

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
	Similar to ``DefaultDict``, but a ``list``.

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


class __BaseContainer(object):

	@classmethod
	def _class_children(cls):
		"""
		The method returning a set of fields/methods defined in the class itself.
		It's used to prevent users from overriding those children with their own
		items of the same name.
		"""
		res = set(dir(cls))  # type: _t.Set[str]
		return res

	@staticmethod
	def _proper_name_base(
		name,  # type: _str_hint
		class_reserved_children,  # type: _t.Set[_str_hint]
		seen_set,  # type: _t.Set[_str_hint]
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

		# print 'base _container_proper_name({}, {}, {}, {})'.format(
		# 	repr(name), repr(class_reserved_children),
		# 	repr(seen_set), repr(seen_set_add)
		# )
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

	@classmethod
	def _check_name_base(
		cls,
		name,  # type: _str_hint
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

		# print 'base _container_check_name({}, {}, {}, {})'.format(
		# 	repr(name), repr(class_reserved_children),
		# 	repr(seen_set), repr(seen_set_add)
		# )
		if not isinstance(name, _str_t):
			raise TypeError(
				"This can't be the name of the {cls_nm}'s member: {itm_nm}".format(
					cls_nm=cls.__name__, itm_nm=repr(name)
				)
			)
		if not name:
			raise ValueError(
				"The {cls_nm}'s member can't have an empty name.".format(
					cls_nm=cls.__name__
				)
			)

		if name[0] not in _var_name_start_chars:
			raise ValueError(
				"This can't be the name of the {cls_nm}'s member "
				"since it starts from an unsupported character: {itm_nm}".format(
					cls_nm=cls.__name__, itm_nm=name
				)
			)
		if not all(
			c in _var_name_chars for c in name[1:]
		):
			raise ValueError(
				"This can't be the name of the {cls_nm}'s member "
				"since it contains an unsupported character: {itm_nm}".format(
					cls_nm=cls.__name__, itm_nm=name
				)
			)
		if not isinstance(name, str):
			name = str(name)

		if name in class_reserved_children:
			raise ValueError(
				"This name can't be used as the {cls_nm}'s member "
				"since the {cls_nm} object already has a class attribute "
				"with the same name: {itm_nm}".format(
					cls_nm=cls.__name__, itm_nm=name
				)
			)
		if name in seen_set:
			raise ValueError(
				"Attempt to add the same {cls_nm}'s member "
				"multiple times at once: {itm_nm}".format(
					cls_nm=cls.__name__, itm_nm=name
				)
			)
		seen_set_add(name)

		return name

	def _check_no_clash_base(
		self,
		name,  # type: _str_hint
		class_reserved_children,  # type: _t.Set[str]
	):

		# print "base._check_no_clash_base({}, {}, {})".format(
		# 	repr(name), repr(class_reserved_children), repr(instance)
		# )
		if not (name and isinstance(name, str)):
			raise ValueError(
				"{cls_nm}'s member can't have this name: {item_nm}".format(
					cls_nm=self.__class__.__name__,
					item_nm=repr(name)
				)
			)
		if name in class_reserved_children:
			raise ValueError(
				"The {cls_nm}'s class member {item_nm} is overridden "
				"on the instance: {inst}".format(
					cls_nm=self.__class__.__name__,
					item_nm=repr(name),
					inst=self
				)
			)
		return name


class Container(__BaseContainer):
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
		check_f = cls._check_name_base
		return (
			(
				check_f(k, class_children, seen, seen_add),
				v
			) for k, v in kwargs.iteritems()
		)

	def __init__(self, **children):
		super(Container, self).__init__()
		self.__dict__.update(
			dict(self.__proper_items(children))
		)

	def iteritems(self):
		class_children = self.__class__._class_children()
		check_f = self._check_no_clash_base
		return (
			(check_f(k, class_children), v)
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
			dict(self.__proper_items(children))
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


class Enum(__BaseContainer):
	"""
	A modified version of ``Container`` class
	designed specifically as an enum-style object which values are ints.

	=======
	Simple usage
	=======

	::

		my_enum = Enum('MyEnum', -1)
			# -1 is the value of a default item. It should be the 1st one attached.
		my_enum.DEFAULT = -1
		my_enum.AAA = 1
		my_enum.BBB = 2

	=======
	Recommended usage
	=======

	For performance reasons, the members of an enum need to be internally cached
	before they can be used. If they are added the simple way (above example),
	all the enum-members are re-cached each time you add a new one.
	Using the ``with`` statement, you can avoid unnecessary re-caching,
	building a list of members to add and then caching them all at once:

	::

		with Enum('MyEnum', -1) as my_enum:
			my_enum.DEFAULT = -1
			my_enum.AAA = 1
			my_enum.BBB = 2

	Note however, that any error-checks are performed only at the caching stage,
	and caching itself is performed on the exit from the ``with`` block.
	So if there is any error with any attached member,
	all the members in a batch are lost.

	But you should debug all enums prior to execution anyway, so this behavior
	shouldn't be an issue.

	"""

	# region Error-checkers for members being added

	@classmethod
	def __check_errors(
		cls,
		name,  # type: str
		value,  # type: int
		enum_nm,  # type: _t.Optional[_str_hint]
		seen_values_set,  # type: _t.Set[int]
		seen_values_set_add,  # type: _t.Callable[[int], None]
		seen_values_dict  # type: _t.Dict[int, str]
	):
		if not isinstance(value, int):
			raise TypeError(
				"{cls_nm}{enum_args} member {nm} should have int value. "
				"Got: {v}".format(
					cls_nm=cls.__name__,
					enum_args='({})'.format(repr(enum_nm)) if enum_nm else '',
					nm=repr(name), v=repr(value)
				)
			)
		if value in seen_values_set:
			raise ValueError(
				"{cls_nm}{enum_args} can't have multiple members with the same value: "
				"{clashing_names} -> {v}".format(
					cls_nm=cls.__name__,
					enum_args='({})'.format(repr(enum_nm)) if enum_nm else '',
					clashing_names='({}, {})'.format(seen_values_dict[value], name),
					v=repr(value)
				)
			)
		seen_values_set_add(value)
		seen_values_dict[value] = name
		return value

	@classmethod
	def __check_item(
		cls,
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
		name = cls._check_name_base(
			name, class_reserved_children, seen_keys_set, seen_keys_set_add
		)
		check_f = cls.__check_errors
		return (
			name,
			check_f(
				name, value, enum_nm, seen_values_set, seen_values_set_add,
				seen_values_dict
			)
		)

	def __check_no_clash(
		self,
		name,  # type: _str_t
		value,  # type: int
		enum_nm,  # type: _t.Optional[_str_hint]
		class_reserved_children,  # type: _t.Set[str]
		seen_values_set,  # type: _t.Set[int]
		seen_values_set_add,  # type: _t.Callable[[int], None]
		seen_values_dict,  # type: _t.Dict[int, str]
	):
		name = self._check_no_clash_base(
			name, class_reserved_children
		)
		check_f = self.__class__.__check_errors
		return (
			name,
			check_f(
				name, value, enum_nm, seen_values_set, seen_values_set_add,
				seen_values_dict
			)
		)

	# endregion

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
		class_children = cls._class_children()
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
		print_on_cache=False,
		**children  # type: int
	):
		"""

		:param name: An optional name of the enum.
		:param default: A value of the enum member used as a default mode.
		:param print_on_cache:
			Print a message when enum members are cached.
			Used for debug purposes only.
		:param children: enum members added right at the initialization.
		"""
		super(Enum, self).__init__()
		if not(name is None or isinstance(name, _str_t)):
			name = repr(name)

		# since we're overriding the __setattr__() method to make it
		# perform extra checks and/or handle batch-caching,
		# we need to manually mark the class instance to indicate
		# it's class itself who's attempting to set internal values. So:
		self.__internal_assign = True

		self.__print_on_cache = bool(print_on_cache)
		self.__pending_batches = None  # type: _h_batches

		self.__enum_name = name  # type: _t.Optional[_str_hint]
		self.__enum_default_val = default
		self.__enum_default_key = ''
		self.__enum_dict = dict()  # type: _t.Dict[str, int]
		self.__all_keys = frozenset()  # type: _t.FrozenSet[str]
		self.__all_values = frozenset()  # type: _t.FrozenSet[int]
		self.__key_mappings = dict()  # type: _t.Dict[int, str]

		self.__internal_assign = False

		if children:
			self.__dict__.update(
				dict(self.__class__.__proper_items(children, name))
			)
			self.__cache_members()

	# to avoid getting stuck in a loop trying to set an internal value
	# while __internal_assign isn't set yet and therefore can't be tested,
	# we need to explicitly tell the names of those very initial member names,
	# to skip all the checks and perform a default assignment:
	__allowed_internal_names = frozenset({
		'__doc__',  # let a user to add a custom docstring, also skipping any checks
		'__internal_assign',
		'_Enum__internal_assign',
	})

	# the full list of internal attributes is used to filter them out
	# from listing all the attached members:
	__internal_names = frozenset({
		'_Enum__doc__',
		'_Enum__print_on_cache',
		'_Enum__pending_batches',
		'_Enum__enum_name',
		'_Enum__enum_default_val',
		'_Enum__enum_default_key',
		'_Enum__enum_dict',
		'_Enum__all_keys',
		'_Enum__all_values',
		'_Enum__key_mappings',
	}.union(__allowed_internal_names))

	def __cache_members(self):
		"""
		After all the enum-members are added, error-check and cache them internally
		to make them appear in the built-in enum methods.

		This step is necessary for the performance reasons: it's much better
		to perform all the error-checks and cache all the members once,
		as the last stage of an enum setup, and work with them later using fast
		hash-sets, rather then perform these checks each time a member is accessed.
		"""
		items = sorted(self.__iteritems_no_cache())

		self.__internal_assign = True
		self.__enum_dict = dict(items)  # type: _t.Dict[str, int]
		self.__all_keys = frozenset(k for k, v in items)  # type: _t.FrozenSet[str]
		self.__all_values = frozenset(v for k, v in items)  # type: _t.FrozenSet[int]
		self.__key_mappings = {v: k for k, v in items}  # type: _t.Dict[int, str]
		if self.__all_values:
			# make sure the default value is actually in the set,
			# if we do have any members defined already
			if self.__enum_default_val not in self.__all_values:
				self.__enum_default_val = sorted(self.__all_values)[0]
			self.__enum_default_key = self.__key_mappings[self.__enum_default_val]
		else:
			self.__enum_default_key = ''
		self.__internal_assign = False

		if self.__print_on_cache and self.__all_keys:
			print ('{} set up with members:\n\t{}'.format(
				self,
				', '.join(self.__all_keys)
			))

	def __iteritems_no_cache(self):
		"""
		An iterator over raw enum items. Unlike public methods, this one doesn't
		use any caches and iterate over members actually found on the enum instance.

		Should be used only internally to actually build those caches, since
		this method is much slower.
		"""
		class_children = self.__class__._class_children()
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
				seen_v, seen_v_add, seen_v_dict
			) for k, v in gen
		)

	def name(
		self,
		value  # type: int
	):
		"""
		Given the value of an enum-member, get it's name.

		If enum doesn't have a member with this value, no error is thrown,
		but the default member's name is returned.

		If there are no members at all (an empty enum), an empty string is returned.
		"""
		if value in self.__all_values:
			return self.__key_mappings[value]
		return self.__enum_default_key

	@property
	def all_names(self):
		"""A set containing **names** of all the enum's members."""
		return self.__all_keys

	@property
	def all_values(self):
		"""A set containing **values** of all the enum's members."""
		return self.__all_values

	@property
	def enum_name(self):
		return self.__enum_name

	def iteritems(self):
		"""A name-value iterator over all the enum members."""
		return self.__enum_dict.iteritems()

	def __setattr__(
		self,
		key,  # type: _str_hint
		value
	):
		# it's important to have key-check first,
		# because this method is called during assignments from the init method.
		if (key in self.__allowed_internal_names) or self.__internal_assign:
			super(Enum, self).__setattr__(key, value)
			return

		if self.__pending_batches:
			self.__pending_batches[-1][key] = value
			return

		# perform check if not batch-assignment:
		key, value = list(
			self.__class__.__proper_items({key: value}, self.__enum_name)
		)[0]
		# print ('{} -> {}'.format(key, value))
		super(Enum, self).__setattr__(key, value)
		self.__cache_members()

	def __repr__(self):
		enum_name = self.__enum_name
		return '<{cls}({nm})>'.format(
			cls=self.__class__.__name__,
			nm='' if (enum_name is None) else repr(enum_name),
		)

	def __getitem__(
		self,
		key  # type: str
	):
		if key in self.__all_keys:
			return self.__enum_dict[key]
		return self.__enum_default_val

	def __contains__(self, item):
		return self.__all_values.__contains__(item)

	def __iter__(self):
		return self.__all_values.__iter__()  # type: _t.Iterator[int]

	def __enter__(self):
		# first, let's cache already added batches if there are any - in case
		# of nested 'with' statements":
		while self.__pending_batches:
			self.__exit__(None, None, None)

		self.__internal_assign = True
		self.__pending_batches = list()  # type: _h_batches
		self.__internal_assign = False
		self.__pending_batches.append(_OrderedDict())

		return self

	def __exit__(
		self,
		exc_type,  # type: _t.Optional[_t.Type[Exception]]
		exc_val,  # type:  _t.Optional[Exception]
		exc_tb  # type: _t.Optional[_ts.TracebackType]
	):
		# in case a user had (for some odd reason) nested the same Enum into
		# multiple 'with' statements, there could be a stack of batches.
		# now, we treat only the last one:
		if self.__pending_batches:
			batch = self.__pending_batches.pop()
			if batch:
				self.__dict__.update(dict(
					self.__class__.__proper_items(batch, self.__enum_name)
				))
				self.__cache_members()

		# ... and clean-up if the batch was indeed the only one
		if not self.__pending_batches:
			self.__internal_assign = True
			self.__pending_batches = None
			self.__internal_assign = False
