"""
A module containing various advanced collections designed to be used as
wrappers of some sort.
"""

__author__ = 'Lex Darlog (DRL)'
__all__ = (
	'DefaultTuple', 'DefaultList', 'Container'
)

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from .py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)

import string as __string
from collections import Iterable as _Iterable

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


class _BaseContainer(object):

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


class Container(_BaseContainer):
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
