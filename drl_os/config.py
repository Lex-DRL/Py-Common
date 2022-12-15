# encoding: utf-8
"""
"""

__author__ = 'Lex Darlog (DRL)'

# built-ins:
from collections import namedtuple as _namedtuple
from dataclasses import dataclass as _dataclass
import errno as _errno
from copy import copy as _copy
import json as _json
from os import (
	path as _path,
	makedirs as _makedirs,
)

# external packages:
try:
	import cattrs as _c
	_cattrs_import_error = None
except ImportError as e:
	_cattrs_import_error = e

# internal packages:
from drl_py23 import to_str_or_unicode as _to_str

# typing:
try:
	from typing import (
		Any as _Any,
		Optional as _O,
		Union as _U,
		Type as _Type,
		TypeVar as _TypeVar,
		Protocol as _Protocol,
		Callable as _Callable,
		List as _List,
		Tuple as _Tuple,
		Set as _Set,
		Iterable as _Iterable,
		NamedTuple as _NamedTuple,

		Dict as _Dict,
		ItemsView as _ItemsView,

		TextIO as _TextIO,
		BinaryIO as _BinaryIO,
	)

	# noinspection PyTypeHints
	_T = _TypeVar('T')
	_C = _TypeVar("_C", bound=type)
	_t_json_dict = _Dict[str, _Any]
	_t_file = _U[_TextIO, _BinaryIO]
except ImportError:
	pass


def _expand_attrs_import_error(
	error,  # type: ImportError
	new_msg="{module} package is required for this feature; {msg}",
):
	if not new_msg or new_msg == '{msg}':
		return error

	error = _copy(error)
	msg = error.msg
	try:
		module_nm = error.name
	except AttributeError:
		module_nm = ''
	module_nm = 'a' if not module_nm else "'{}'".format(module_nm)

	msg = new_msg.format(msg=msg, module=module_nm)
	args = list(error.args)
	args[0] = msg
	error.msg = msg
	error.args = tuple(args)
	return error


_cattrs_error = None if _cattrs_import_error is None else _expand_attrs_import_error(_cattrs_import_error)


def config_abs_path(rel_path=''):
	if not rel_path:
		rel_path = ''
	rel_path = _to_str(rel_path).replace('\\', '/')
	has_trailing_slash = rel_path.endswith('/')
	rel_path = rel_path.strip('/')
	rel_path = '~/{pth}'.format(pth=rel_path) if rel_path else '~'

	abs_path = _path.expanduser(rel_path)
	abs_path = _path.abspath(abs_path).replace('\\', '/')

	return type(abs_path)('{pth}{trail}').format(pth=abs_path, trail='/' if has_trailing_slash else '')


class JSONConfigError(ValueError):
	pass


@_dataclass(init=False)
class _JSON:
	encoding = 'utf-8'
	indent = '\t'
	indent_py2 = 1
	user_path = '.drl/config_template'

	def abs_path(self):
		res = config_abs_path(
			self._value_or_call(self.user_path)
		)
		if res.lower().endswith('.json'):
			return res
		return type(res)('{0}.json').format(res)

	__all_args = {'encoding', 'indent', 'indent_py2', 'user_path', 'abs_path'}

	def __init__(
		self,
		json_class,  # type: type
	):
		attr_names = {x for x in dir(json_class) if x in self.__all_args}
		if not any(x in attr_names for x in ['user_path', 'abs_path']):
			raise JSONConfigError("'JSON' class must define either 'user_path' or 'abs_path'")

		for arg_nm in attr_names:
			val = getattr(json_class, arg_nm)
			setattr(self, arg_nm, val)

	@staticmethod
	def _value_or_call(
		value  # type: _U[_Callable[[], _T], _T]
	):
		if callable(value):
			value = value()
		res = value  # type: _T
		return res

	def get(self, attr):
		return self._value_or_call(getattr(self, attr))

	# noinspection PyBroadException
	def _with_file_do_json(
		self,
		func,  # type: _Callable[[_t_file], _T]
		write=False,
	):
		mode = 'w' if write else 'r'
		file_path = self.get('abs_path')
		if write:
			parent_dir = _path.abspath(_path.join(file_path, _path.pardir)).replace('\\', '/')
			if not _path.isdir(parent_dir):
				_makedirs(parent_dir)

		try:
			with open(file_path, '{}t'.format(mode), encoding=self.encoding) as f:
				res = func(f)  # type: _T
				return res
		except Exception:
			pass

		try:
			with open(file_path, '{}t'.format(mode)) as f:
				res = func(f)  # type: _T
				return res
		except Exception as e:
			try:
				with open(file_path, '{}b'.format(mode)) as f:
					res = func(f)  # type: _T
					return res
			except Exception:
				raise e

	def _json_load(self):
		res = self._with_file_do_json(_json.load, write=False)  # type: _t_json_dict
		return res

	# noinspection PyBroadException
	def _json_dump(
		self,
		json_dict  # type: _t_json_dict
	):
		with_file = self._with_file_do_json
		try:
			return with_file(lambda f: _json.dump(json_dict, f, indent=self.indent), write=True)
		except Exception:
			pass

		try:
			return with_file(lambda f: _json.dump(json_dict, f, indent=self.indent_py2), write=True)
		except Exception as e:
			try:
				return with_file(lambda f: _json.dump(json_dict, f), write=True)
			except Exception:
				raise e


_args_excluded = {'JSON', 'json_load', 'json_save'}


@_dataclass(init=False)
class _ConverterObj:
	config_cls = None  # type: _Type[_T]
	json_cls = None  # type: _JSON

	@classmethod
	def __init__(self, config_cls):
		if config_cls is None or type(config_cls) is not type:
			raise JSONConfigError("Internal error: `json_config` decorator can't find the class it's assigned to.")

		try:
			json_cls = config_cls.JSON
		except Exception:
			raise JSONConfigError("{cls} must define inner class named `JSON`".format(cls=config_cls))

		self.config_cls = config_cls
		self.json_cls = _JSON(json_cls)

	def _check_inst(
		self,
		config_inst,  # type: _T
	):
		config_cls = self.config_cls
		if not isinstance(config_inst, config_cls):
			raise JSONConfigError(
				"Internal `json_config` decorator error: {inst} is not an instance of {cls}.".format(
					inst=repr(config_inst), cls=config_cls
				)
			)
		return config_inst

	def _from_json_dict(
		self,
		json_dict,  # type: _t_json_dict
	):
		try:
			return self._check_inst(
				self.config_cls(**json_dict)
			)
		except Exception as e:
			try:
				res = self._check_inst(
					self.config_cls()
				)
				for k, v in json_dict.items():
					setattr(res, k, v)
				return res
			except Exception:
				raise e

	def _to_json_dict(
		self,
		config_inst,  # type: _T
	):
		config_inst = self._check_inst(config_inst)

		all_attrs = set(dir(config_inst))
		private_attrs = {a.strip('_') for a in all_attrs if a.startswith('_')}
		res_map = (
			(a, getattr(config_inst, a)) for a in all_attrs
			if not(a.startswith('_') or a in _args_excluded)
		)
		res = dict()  # type: _t_json_dict
		for attr_nm, val in res_map:
			if callable(val):
				if attr_nm not in private_attrs:
					continue
				val = val()
			res[attr_nm] = val
		return res

	def json_load(
		self,
		create_default_if_missing=True
	):
		try:
			# noinspection PyProtectedMember
			json_dict = self.json_cls._json_load()
		except OSError as e:
			if create_default_if_missing and e.errno == _errno.ENOENT:
				# We've got no config saved yet. Creating a default one.
				res = self.config_cls()  # type: _T
				self.json_save(res)
				return res
			else:
				raise e

		# noinspection PyUnboundLocalVariable
		res = self._from_json_dict(json_dict)  # type: _T
		return res

	def json_save(
		self,
		config_inst,  # type: _T
	):
		json_dict = self._to_json_dict(config_inst)
		# noinspection PyProtectedMember
		self.json_cls._json_dump(json_dict)


class _ConverterAttrs(_ConverterObj):
	def _from_json_dict(
		self,
		json_dict,  # type: _t_json_dict
	):
		res = self._check_inst(
			_c.structure(json_dict, self.config_cls)
		)  # type: _T
		return res

	def _to_json_dict(
		self,
		config_inst,  # type: _T
	):
		return _c.unstructure(
			self._check_inst(config_inst), self.config_cls
		)


class _ConverterAttrsError(_ConverterObj):
	def _from_json_dict(
		self,
		json_dict,  # type: _t_json_dict
	):
		try:
			return super(_ConverterAttrsError, self)._from_json_dict(json_dict)
		except Exception:
			raise _cattrs_error

	def _to_json_dict(
		self,
		config_inst,  # type: _T
	):
		try:
			return super(_ConverterAttrsError, self)._to_json_dict(config_inst)
		except Exception:
			raise _cattrs_error


if _cattrs_error is not None:
	# cannot use
	_ConverterAttrs = _ConverterAttrsError

# noinspection PyBroadException
try:
	# noinspection PyUnboundLocalVariable
	class JsonConfigProto(_Protocol[_T]):
		@classmethod
		def json_load(cls: _Type[_T], create_default_if_missing=True) -> _T:
			...

		def json_save(self: _T):
			...

except Exception:
	pass


def json_config(
	maybe_cls=None,  # type: _C
	*_, attrs=False,
):
	"""
	Decorator which turns a dataclass into a JSON-exportable config. It adds `json_load()`
	and `json_save()` methods.

	You must define in internal class named `JSON` which has to define either `user_path` or `abs_path`
	attribute or function. They define where the config is stored.
	"""

	converter = _ConverterAttrs if attrs else _ConverterObj

	def _wrap(
		maybe_cls  # type: _C
	):
		# noinspection PyDecorator
		@classmethod
		def json_load(cls, create_default_if_missing=True):
			return converter(cls).json_load(create_default_if_missing=create_default_if_missing)

		def json_save(self):
			return converter(self.__class__).json_save(self)

		res = maybe_cls  # type: _U[_C, JsonConfigProto]
		res.json_load = json_load
		res.json_save = json_save
		return res

	if maybe_cls is None:
		return _wrap

	wrapped_res = _wrap(maybe_cls)
	return wrapped_res
