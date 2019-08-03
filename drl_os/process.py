"""
The module providing functionality to kill processes, platform-independently.
"""
__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)

try:
	import psutil
except ImportError:
	try:
		from modules import (
			pip_install as __pip,
			PipError as __pipEr
		)
	except ImportError:
		raise ImportError(
			"Can't continue because <psutil> module is not found "
			"and the py-package able to install it isn't found, too."
		)
	try:
		__pip('psutil')
	except __pipEr:
		__pip('pip psutil')
	import psutil

# noinspection PyBroadException
try:
	_h_l_proc = _t.List[psutil.Process]
	_h_opt_call = _t.Optional[_t.Callable[[psutil.Process], _t.Any]]
	_h_timeout = _t.Optional[_t.Union[int, float]]
except:
	pass

from subprocess import call as _call
import fnmatch as _fm

from . import platform as _pf
from drl_common import errors as _err


def __terminate_arg_cleanup(
	process,  # type: psutil.Process
	timeout,  # type: _h_timeout
	on_terminate  # type: _h_opt_call
):
	_err.WrongTypeError(
		process, psutil.Process, 'process'
	).raise_if_needed()
	if not callable(on_terminate):
		on_terminate = None
	if not(isinstance(timeout, (int, float)) and timeout > 0):
		timeout = None
	return process, timeout, on_terminate


def __terminate_windows(
	process,  # type: psutil.Process
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_terminate=None  # type: _h_opt_call
):
	"""
	High-level method to terminate a process.

	:param process: A process to kill.
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	process, timeout, on_terminate = __terminate_arg_cleanup(
		process, timeout, on_terminate
	)

	cmd = ['taskkill']
	if force:
		cmd.append('/f')
	cmd.extend(['/pid', str(process.pid)])
	whole_tree = list()  # type: _h_l_proc
	if tree:
		whole_tree = process.children(recursive=True)
		cmd.append('/t')
	whole_tree.append(process)
	_call(cmd)

	gone, still_alive = psutil.wait_procs(
		whole_tree, timeout=timeout, callback=on_terminate
	)  # type: _t.Tuple[_h_l_proc, _h_l_proc]
	for p in still_alive:
		p.kill()


def __terminate_unix(
	process,  # type: psutil.Process
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_terminate=None  # type: _h_opt_call
):
	"""
	High-level method to terminate a process.

	:param process: A process to kill.
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	process, timeout, on_terminate = __terminate_arg_cleanup(
		process, timeout, on_terminate
	)
	whole_tree = list()  # type: _h_l_proc
	if tree:
		whole_tree = process.children(recursive=True)
	whole_tree.append(process)

	if not force:
		for p in whole_tree:
			p.terminate()
		gone, still_alive = psutil.wait_procs(
			whole_tree, timeout=timeout, callback=on_terminate
		)  # type: _t.Tuple[_h_l_proc, _h_l_proc]
		whole_tree = still_alive

	for p in whole_tree:
		p.kill()


terminate = __terminate_windows if _pf.IS_WINDOWS else __terminate_unix
terminate.__doc__ = """
High-level method to terminate a process.

:param process: A process to kill.
:param tree: End the entire process tree, with all children.
:param timeout:
	How long to wait for the process to finish (seconds), in graceful-kill mode.
:param force: Instant-kill instead of graceful termination (waiting to end).
:param on_terminate:
	A function which gets called when one of the processes being waited on
	is terminated and a `Process` instance is passed as callback argument.
"""


def __name_match_win(
	name,  # type: _str_hint
	pattern  # type: _str_hint
):
	name = name.replace('\\', '/')
	pattern = pattern.replace('\\', '/')
	return _fm.fnmatch(name, pattern)


_names_match = __name_match_win if _pf.IS_WINDOWS else _fm.fnmatchcase


def _dummy_f(*args, **kwargs):
	pass


def terminate_by_name(
	names,  # type: _t.Union[_str_hint, _t.Iterable[_str_hint]]
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_match=None,  # type: _h_opt_call
	on_terminate=None  # type: _h_opt_call
):
	"""
	Kill all the processes matching to the given filters by name.

	:param names: Filename-filter(s). May contain wildcards ("tool*.exe")
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_match:
		A function which gets called when a matching process is found.
		Receives a `Process` instance.
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	if not callable(on_match):
		on_match = _dummy_f
	for p in psutil.process_iter():
		p_nm = p.name()
		if any(_names_match(p_nm, x) for x in names):
			on_match(p)
			terminate(p, tree, timeout, force, on_terminate)


def terminate_by_path(
	paths,  # type: _t.Union[_str_hint, _t.Iterable[_str_hint]]
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_match=None,  # type: _h_opt_call
	on_terminate=None  # type: _h_opt_call
):
	"""
	Kill all the processes matching to the given filters by the full path.

	:param paths: Filename-filter(s). May contain wildcards ("W:/tool*.exe")
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_match:
		A function which gets called when a matching process is found.
		Receives a `Process` instance.
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	if not callable(on_match):
		on_match = _dummy_f
	for p in psutil.process_iter():
		p_pth = p.exe()
		if any(_names_match(p_pth, x) for x in paths):
			on_match(p)
			terminate(p, tree, timeout, force, on_terminate)
