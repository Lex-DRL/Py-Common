"""
Extra handy functions to work with processes.
"""
__author__ = 'Lex Darlog (DRL)'

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
)

# endregion

from subprocess import (
	call as _call,
	Popen as _Popen,
)

from drl_os.env import add_multi as _add_envs


def start(
	executable,  # type: _t.Union[_str_h, _t.Sequence[_str_h]]
	keep_console_window=False,  # type: bool
	append_env_in_front=False,  # type: bool
	*env_args,  # type: _t.Tuple[_str_h, _t.Optional[_str_h]]
	**env_kwargs
):
	"""
	The function starting a process with (optionally):
		* some command-line arguments
		* setting environment variables (see `drl_os.env.add_multi()` function).
	"""
	_add_envs(append_env_in_front, *env_args, **env_kwargs)

	if keep_console_window:
		return _call(executable)

	_Popen(executable)
	return 0
