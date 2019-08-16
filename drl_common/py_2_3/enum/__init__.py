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
