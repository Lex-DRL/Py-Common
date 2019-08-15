"""A version-independent wrapper module on top of <enum> introduced in 3.4."""

__author__ = 'Lex Darlog (DRL)'

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
		from enum import *
	except (AttributeError, ImportError):
		try:
			__pip_inst('enum34', True, False)
			from enum import *
		except ImportError:
			__pip_inst(['pip', 'enum34'], True, False)
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
		from enum import *

		print (
			'Unable to import a built-in <enum> module or download it '
			'from the internet due to the error: {}\n'
			'Installing a locally cached version: {}.'.format(e, __enum_path)
		)
	except BaseException as e2:
		from .__local_fallback import *
		print (
			'Unable to import a built-in <enum> module '
			'or install it from a local cache due to the errors: {}\n{}\n'
			'Using locally stored copy instead.'.format(e, e2)
		)
