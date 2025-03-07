__author__ = 'Lex Darlog (DRL)'

import collections as _col

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_common.utils import flatten_gen as _flatten
from drl_py23 import (
	str_t as _str_t,
	str_hint as _str_h,
)
from drl_py23.enum import (
	EnumDefault as __EnumDefault,
	override_default as __default,
)


@__default(0)
class PipErrorType(__EnumDefault):
	"""
	Supported modes of `PipError`.
	"""
	CUSTOM = -1  # type: PipErrorType
	NO_PIP = 1  # type: PipErrorType
	MODULE_CANT_IMPORT = 2  # type: PipErrorType

	# default:
	UNKNOWN = 0  # type: PipErrorType


class PipError(ImportError):
	"""
	A subset of `ImportError` signaling that there was some error with pip.
	"""

	# noinspection PyShadowingBuiltins
	def __init__(
		self,
		message='',  # type: _str_h
		type=PipErrorType.UNKNOWN  # type: _t.Union[PipErrorType, _str_h, int]
	):
		super(PipError, self).__init__(message)
		self.__type = PipErrorType.get(type)  # type: PipErrorType
		self.args = (message, self.__type)

	@property
	def type(self):
		return self.__type


# noinspection PyIncorrectDocstring
def pip_install(
	module_names,  # type: _t.Union[_str_h, _t.Iterable[_str_h]]
	upgrade=True,
	force_reinstall=False
):
	# noinspection SpellCheckingInspection
	"""
	A wrapper function, installing a module(s) via PIP in a convenient way,
	regardless of the Python and PIP version.

	https://pip.pypa.io/en/stable/installing/

	:param module_names:
		Either an iterable of strings or a single string with module names
		separated by a whitespace.

		You can pass a single module:
			``pip_install('chardet')``

		... a list of modules installed/updated in the given order:
			``pip_install('chardet tzlocal')``

		... and even update the PIP itself by passing it as the 1st module:
			``pip_install('pip chardet tzlocal')``
		"""

	def _cleanup_names_arg_gen(names):
		"""
		Initial cleanup of provided module names.
		The resulting sequence is generator.
		"""
		if isinstance(names, _str_t):
			names = names.split()
		if not isinstance(names, (_col.Iterable, _col.Iterator)):
			return

		for arg1 in _flatten(filter(None, names)):
			if not isinstance(arg1, _str_t):
				continue
			arg1 = arg1.strip()
			if not arg1:
				continue

			# We may need to split the given strings to multiple arguments.
			# But many of the common separators may actually be used with intention:
			# pip install SomePackage-1.0-py2.py3-none-any.whl
			# pip install 'SomePackage>=1.0.4'
			# pip install 'SomeProject[foo, bar]'
			# pip install 'SomeProject >=1.2,<2.0'

			# So, the only possible separators left are:
			for arg2 in arg1.split(';|'):
				arg2 = arg2.strip()
				if not arg2:
					continue
				yield arg2

	module_names = list(_cleanup_names_arg_gen(module_names))

	if not module_names:
		return

	# TODO: detect which modules need to be installed (not upgraded) by trying to import them

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
		try:
			# noinspection PyProtectedMember
			from pip import _internal as pip_internal
			main_f = pip_internal.main
		except (AttributeError, ImportError):
			raise PipError(
				"PIP isn't installed or can't be found", type=PipErrorType.NO_PIP
			)
	main_f(pip_args)

	try:
		# noinspection PyUnresolvedReferences
		import importlib
	except ImportError:
		# there's no importlib module.
		# So let's just assume everything went ok, with no check:
		return

	def is_imported_ok(module_name):
		try:
			importlib.import_module(module_name)
			return True
		except ImportError:
			return False

	not_importable = [
		mdl for mdl in module_names
		if not is_imported_ok(mdl)
	]

	if not_importable:
		raise PipError(
			"The following modules can't be imported. "
			"Probably because they were just installed by PIP and "
			"Python interpreter needs to be restarted first:\n" + '\n'.join(not_importable),
			PipErrorType.MODULE_CANT_IMPORT
		)
