__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	from typing import *
except ImportError:
	pass
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)


class PipError(ImportError):
	"""
	A subset of `ImportError` signaling that there was some error with pip.
	"""
	pass


# noinspection PyIncorrectDocstring
def pip_install(
	module_names,  # type: Union[_str_hint, Iterable[_str_hint]]
	upgrade=True,
	force_reinstall=False
):
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
	if isinstance(module_names, _str_t):
		module_names = module_names.split()
	module_names = filter(None, module_names)
	module_names = [
		(
			m if isinstance(m, _str_t) else str(m)
		).strip()
		for m in module_names
	]  # type: List[_str_hint]
	module_names = filter(None, module_names)

	# TODO: there's only basic clean-up and split by spaces.
	# TODO: Should also handle commas and dots.

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
			raise PipError("PIP isn't installed or can't be found")
	main_f(pip_args)

	try:
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
			"Python interpreter needs to be restarted first:\n" + '\n'.join(not_importable)
		)
