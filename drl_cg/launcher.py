"""
Service functions launching a CG package with some modifications.
"""

__author__ = 'Lex Darlog (DRL)'

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_h
)

# endregion

from subprocess import (
	call as _call,
	Popen as _Popen,
)
from drl_os.process import add_envs as _add_envs

# noinspection PyBroadException
try:
	import win_unicode_console
	_unicode_console = True
except:
	_unicode_console = False


def with_envs(
	executable,  # type: _t.Union[_str_h, _t.Sequence[_str_h]]
	keep_console_window,  # type: bool
	append_in_front,  # type: bool
	*envs  # type: _t.Tuple[_str_h, _t.Optional[_str_h]]
):
	"""
	Sets given environment variables for the current session only and
	starts the given program.

	:param executable:
		Path to the program binary (with optional arguments).
		The syntax is the same as for `subprocess.call`.
	:param keep_console_window:
		When `True`, the program is started with `subprocess.call` which keeps
		the console window open. Otherwise, the it's run with `subprocess.Popen`
		which closes the console window as soon as the program is launched.
	:param append_in_front: see drl_os.process.add_envs()
	:param envs: see drl_os.process.add_envs()
	:return: return-code of `subprocess.call` or 0 if `subprocess.Popen` is used
	"""
	_add_envs(append_in_front, *envs)
	if _unicode_console:
		win_unicode_console.enable()

	if keep_console_window:
		return _call(executable)

	_Popen(executable)
	return 0
