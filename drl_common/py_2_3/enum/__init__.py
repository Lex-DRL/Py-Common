"""A version-independent wrapper module on top of <enum> introduced in 3.4."""

__author__ = 'Lex Darlog (DRL)'

# based on v1.1.6:
__all__ = ['Enum', 'IntEnum', 'unique', 'EnumDefault', 'override_default']

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from ..__str_typing import (
	str_t as _str_t,
	str_hint as _str_hint
)


def __pip_inst(
	module_names,  # type: _t.Union[_str_hint, _t.Iterable[_str_hint]]
	upgrade=True,
	force_reinstall=False
):
	"""
	A simplified version of ``pip_install``, to avoid recursive dependencies.
	"""
	if isinstance(module_names, _str_t):
		module_names = module_names.split()
	module_names = filter(None, module_names)

	pip_args = [
		arg for arg, do_arg in (
			('install', True),
			('--upgrade', upgrade),
			('--force-reinstall', force_reinstall),
		) if do_arg
	]
	pip_args += module_names

	try:
		import pip
		# noinspection PyUnresolvedReferences
		main_f = pip.main
	except (AttributeError, ImportError):
		# noinspection PyProtectedMember
		from pip import _internal as pip_internal
		main_f = pip_internal.main
	main_f(pip_args)


try:
	try:
		import enum as _enum_module
		from enum import *
	except (AttributeError, ImportError):
		try:
			__pip_inst('enum34', True, False)
			import enum as _enum_module
			from enum import *
		except ImportError:
			__pip_inst(['pip', 'enum34'], True, False)
			import enum as _enum_module
			from enum import *
except BaseException as e:
	try:
		from os import path as __pa
		import sys as __sys

		__enum_path = __pa.join(
			__pa.dirname(__pa.abspath(__file__)),
			'__whl_cache',
			(
				'enum34-1.1.6-py3-none-any.whl'
				if __sys.version_info[0] > 2
				else 'enum34-1.1.6-py2-none-any.whl'
			)
		)
		__pip_inst([__enum_path], True, True)
		import enum as _enum_module
		from enum import *

		print (
			'Unable to import a built-in <enum> module or download it '
			'from the internet due to the error: {}\n'
			'Installing a locally cached version: {}.'.format(e, __enum_path)
		)
	except BaseException as e2:
		from . import __local_fallback as _enum_module
		from .__local_fallback import *
		print (
			'Unable to import a built-in <enum> module '
			'or install it from a local cache due to the errors: {}\n{}\n'
			'Using locally stored copy instead.'.format(e, e2)
		)


@unique
class EnumDefault(IntEnum):
	"""
	An extension of ``IntEnum`` with ``unique`` decorator, providing the ``get()``
	method.
	It allows you to fall back to a default enum member if you try to query a key
	(a name or int-value) of a member that this Enum doesn't have.

	The default member is the one with the smallest int value (incl. negative).
	But you can override that using the ``override_default`` decorator:

	=======
	Example
	=======

	::

		@override_default(3)
		class TestEnum(EnumDefault):
			BBB = 2
			CCC = 3  # will be set as default
			ZZZ = -17
			AAA = 1
			DDD = 4

	"""

	def __init__(self, *args, **kwargs):

		# print (self, type(self), self.__dict__)
		# print (self.__class__, type(self.__class__))
		# print (self.__class__.__dict__)
		# print (args)
		# print (kwargs)
		# print ('\n')

		super(EnumDefault, self).__init__(*args, **kwargs)
		if not self.__is_init():
			self.__cls_init()
		cur_default = self.__get_default()
		if cur_default is None or self.value < cur_default.value:
			self._set_default(self)
		self.__append_member(self)

	@classmethod
	def __cls_init(cls):
		"""Initialize the inherited class."""

		# noinspection PyBroadException
		try:
			_h_enum_key = _t.Union[_str_hint, EnumDefault, int]
		except:
			pass
		# print ('{} initialization'.format(cls))
		cls.__default = None
		cls.__all_members = frozenset()  # type: _t.FrozenSet[EnumDefault]
		cls.__all_ordered = tuple()  # type: _t.Tuple[EnumDefault, ...]
		cls.__all_keys = frozenset()  # type: _t.FrozenSet[_h_enum_key]
		cls.__key_mappings = dict()  # type: _t.Dict[_h_enum_key, EnumDefault]

	@classmethod
	def __is_init(cls):
		"""
		Whether the inherited class is initialized.
		It may be not if the class has no enum-members.
		"""
		try:
			val = cls.__default
			return True
		except AttributeError:
			return False

	@classmethod
	def __get_default(cls):
		"""Used to get the default value on an instance."""
		return cls.__default  # type: EnumDefault

	@classmethod
	def _set_default(cls, val):
		"""Set the default enum member (instance). No checks."""
		cls.__default = val

	@classmethod
	def default(cls):
		"""The default Enum member."""
		if not cls.__is_init():
			cls.__cls_init()
		res = cls.__default  # type: _t.Optional[EnumDefault]
		return res

	@classmethod
	def all_members(cls):
		"""A ``frozenset`` containing all the registered Enum members."""
		if not cls.__is_init():
			cls.__cls_init()
		res = cls.__all_members  # type: _t.FrozenSet[EnumDefault]
		return res

	@classmethod
	def all_members_ordered(cls):
		"""A frozen set containing all the registered Enum members."""
		if not cls.__is_init():
			cls.__cls_init()
		res = cls.__all_ordered  # type: _t.Tuple[EnumDefault, ...]
		return res

	@classmethod
	def __append_member(
		cls,
		member  # type: EnumDefault
	):
		"""Attach a newly added member to all the internal cache-sets."""
		tmp_set = set(cls.__all_members)
		tmp_set.add(member)
		cls.__all_members = frozenset(tmp_set)  # type: _t.FrozenSet[EnumDefault]

		nm = member.name  # type: _str_hint
		int_val = member.value  # type: int
		keys = {member, nm, int_val}
		tmp_set = set(cls.__all_keys)
		tmp_set = tmp_set.union(keys)
		cls.__all_keys = frozenset(tmp_set)

		for k in keys:
			cls.__key_mappings[k] = member

		tmp_lst = list(cls.__all_ordered)
		tmp_lst.append(member)
		cls.__all_ordered = tuple(tmp_lst)  # type: _t.Tuple[EnumDefault, ...]

	@property
	def name(self):
		""""The name of enum member."""
		res = super(EnumDefault, self).name  # type: _str_hint
		return res

	@property
	def value(self):
		""""The actual ``int`` value of enum member."""
		res = super(EnumDefault, self).value  # type: int
		return res

	@classmethod
	def get(
		cls,
		key,  # type: _t.Union[_str_hint, IntEnum, int]
		default=None  # type: _t.Optional[EnumDefault]
	):
		"""
		An error-safe method, returning an Enum member from any of:
			* member name
			* the member (enum-instance) itself
			* member int-value

		If provided enum identifier not found, return the default member.
		On attempt to pass another enum's member as a key, first it's name used
		and if not found, then it's int value.

		If optional ``default`` argument provided, (the current enum's member), use
		it. Otherwise, the enum's global default member (the 1st one added) is used.
		"""
		if (not cls.__is_init()) or cls.__default is None:
			raise AttributeError('{} has no members.'.format(cls))
		if isinstance(key, IntEnum) and not isinstance(key, cls):
			nm = key.name  # type: _str_hint
			key = nm if (nm in cls.__all_keys) else key.value
		if default is None or not isinstance(default, cls):
			default = cls.__default
		res = (
			cls.__key_mappings[key] if key in cls.__all_keys else default
		)  # type: EnumDefault
		return res

	@classmethod
	def item_name(
		cls,
		key,  # type: _t.Union[_str_hint, IntEnum, int]
		default=None  # type: _t.Optional[EnumDefault]
	):
		return cls.get(key, default=default).name

	@classmethod
	def item_value(
		cls,
		key,  # type: _t.Union[_str_hint, IntEnum, int]
		default=None  # type: _t.Optional[EnumDefault]
	):
		return cls.get(key, default=default).value


def override_default(
	item_id  # type: int
):
	def set_default_id(
		cls,  # type: _t.Type[EnumDefault]
	):
		# print (cls, item_id)
		if isinstance(item_id, int):
			cls._set_default(cls.get(item_id))
		return cls
	return set_default_id


###############################################################################
# first attempt to create a universal enum. Here as a git backup just in case:


import types as _ts
from collections import OrderedDict as _OrderedDict
from drl_common.cols import _BaseContainer

# noinspection PyBroadException
try:
	_h_enum_batch = _t.Dict[str, _t.Any]
	_h_enum_batches = _t.Optional[_t.List[_h_enum_batch]]
except:
	pass


class _OldEnum_bak(_BaseContainer):
	"""
	A modified version of ``Container`` class
	designed specifically as an enum-style object which values are ints.

	=======
	Simple usage
	=======

	::

		my_enum = _OldEnum_bak('MyEnum', -1)
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

		with _OldEnum_bak('MyEnum', -1) as my_enum:
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
		super(_OldEnum_bak, self).__init__()
		if not(name is None or isinstance(name, _str_t)):
			name = repr(name)

		# since we're overriding the __setattr__() method to make it
		# perform extra checks and/or handle batch-caching,
		# we need to manually mark the class instance to indicate
		# it's class itself who's attempting to set internal values. So:
		self.__internal_assign = True

		self.__print_on_cache = bool(print_on_cache)
		self.__pending_batches = None  # type: _h_enum_batches

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

	def supp_name(self, name):
		"""
		Ensure that the given name is one of enum's members.
		If not, use the default one.
		"""
		if name in self.__all_keys:
			return name
		return self.__enum_default_key

	def supp_value(self, val):
		"""
		Ensure that the given value is one of enum's members.
		If not, use the default one.
		"""
		if val in self.__all_values:
			return val
		return self.__enum_default_val

	@property
	def all_names(self):
		"""A set containing **names** of all the enum's members."""
		return self.__all_keys  # type: _t.FrozenSet[str]

	@property
	def all_values(self):
		"""A set containing **values** of all the enum's members."""
		return self.__all_values  # type: _t.FrozenSet[int]

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
			super(_OldEnum_bak, self).__setattr__(key, value)
			return

		if self.__pending_batches:
			self.__pending_batches[-1][key] = value
			return

		# perform check if not batch-assignment:
		key, value = list(
			self.__class__.__proper_items({key: value}, self.__enum_name)
		)[0]
		# print ('{} -> {}'.format(key, value))
		super(_OldEnum_bak, self).__setattr__(key, value)
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

	def __eq__(self, other):
		if not isinstance(other, _OldEnum_bak):
			return False
		return (
			self.__enum_dict == other.__enum_dict and
			self.__enum_default_val == other.__enum_default_val
		)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __iter__(self):
		return self.__all_values.__iter__()  # type: _t.Iterator[int]

	def __enter__(self):
		# first, let's cache already added batches if there are any - in case
		# of nested 'with' statements":
		while self.__pending_batches:
			self.__exit__(None, None, None)

		self.__internal_assign = True
		self.__pending_batches = list()  # type: _h_enum_batches
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
