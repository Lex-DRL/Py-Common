__author__ = 'DRL'

py2 = False
py3 = False

try:
	# support type hints:
	import typing
	py3 = True
except ImportError:
	import __empty_module as typing
	py2 = True
	py3 = False

try:
	from itertools import izip, izip_longest
except ImportError:
	izip = zip
	izip_longest = zip_longest


str_t = [str]
# noinspection PyBroadException,PyPep8
try:
	if unicode not in str_t:
		str_t += [unicode]
except:
	pass
# noinspection PyBroadException,PyPep8
try:
	if bytes not in str_t:
		str_t += [bytes]
except:
	pass
str_t = tuple(str_t)  # type: typing.Tuple[typing.Type[str], typing.Type[unicode]]

# noinspection PyBroadException,PyPep8
try:
	t_strict_unicode = unicode
	t_strict_str = str
except:
	t_strict_unicode = str
	t_strict_str = bytes

# noinspection PyBroadException,PyPep8
try:
	str_hint = typing.Union[str, unicode]
except:
	# noinspection PyBroadException,PyPep8
	try:
		str_hint = typing.Union[str, bytes]
	except:
		str_hint = str

# noinspection PyBroadException,PyPep8
# try:
# 	str_hint = typing.Union[str_hint, typing.AnyStr]
# except:
# 	pass


def __pip_inst(
	module_names,  # type: typing.Union[str_hint, typing.Iterable[str_hint]]
	upgrade=True,
	force_reinstall=False
):
	"""
	A simplified version of ``pip_install``, to avoid recursive dependencies.
	"""
	if isinstance(module_names, str_t):
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
		import enum
	except (AttributeError, ImportError):
		try:
			__pip_inst('enum34', True, False)
			import enum
		except ImportError:
			__pip_inst(['pip', 'enum34'], True, True)
			import enum
except BaseException as e:
	try:
		from os import path as __pa
		import sys as __sys

		__enum_path = __pa.join(
			__pa.dirname(__pa.abspath(__file__)),
			'__local_cache',
			(
				'enum34-1.1.6-py3-none-any.whl'
				if __sys.version_info[0] > 2
				else 'enum34-1.1.6-py2-none-any.whl'
			)
		)
		__pip_inst([__enum_path], True, True)
		import enum

		print (
			'Unable to import a built-in <enum> module or download it '
			'from the internet due to the error: {}\n'
			'Installing a locally cached version: {}.'.format(e, __enum_path)
		)
	except BaseException as e2:
		from .__local_fallback import enum
		print (
			'Unable to import a built-in <enum> module '
			'or install it from a local cache due to the errors: {}\n{}\n'
			'Using locally stored copy instead.'.format(e, e2)
		)
