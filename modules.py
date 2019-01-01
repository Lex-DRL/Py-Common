__author__ = 'DRL'

try:
	# support type hints in Python 3:
	from typing import *
	unicode = str  # fix errors in Python 3
except ImportError:
	pass


def pip_install(
	module_names,  # type: Union[str, unicode, Iterable[Union[str, unicode]]]
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
	if isinstance(module_names, (str, unicode)):
		module_names = module_names.split()
	module_names = filter(None, module_names)
	module_names = [
		(
			m if isinstance(m, (str, unicode)) else str(m)
		).strip()
		for m in module_names
	]  # type: List[Union[str, unicode]]
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
		pip.main(pip_args)
	except AttributeError:
		from pip import _internal as pip_internal
		pip_internal.main(pip_args)
