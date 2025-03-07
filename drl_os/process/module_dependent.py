"""
Extra functions, depending on some external modules that require install.
They're installed automatically using pip, if possible.
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
	str_h_o as _str_h_o,
)

# endregion

try:
	import psutil
except ImportError:
	try:
		from modules import (
			pip_install as __pip,
			PipError as __pipEr,
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
	_h_arg_proc = _t.Union[int, psutil.Process]
	_h_arg_proc = _t.Union[_h_arg_proc, _t.Iterable[_h_arg_proc]]
	_h_arg_nm = _t.Union[int, float, psutil.Process, _str_h]
	_h_arg_nm = _t.Union[_h_arg_nm, _t.Iterable[_h_arg_nm]]
	_h_l_proc = _t.List[psutil.Process]
	_h_s_proc = _t.Set[psutil.Process]
	_h_opt_call = _t.Optional[_t.Callable[[psutil.Process], _t.Any]]
	_h_timeout = _t.Optional[_t.Union[int, float]]
except:
	pass

import fnmatch as _fm
from subprocess import (
	call as _call,
	Popen as _Popen,
)

from drl_os import platform as _pf
from drl_common import errors as _err


def __terminate_windows(
	root_processes,  # type: _h_l_proc
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_terminate=None  # type: _h_opt_call
):
	"""
	Low-level method to terminate a list of processes.

	:param root_processes: A process list to kill.
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	whole_tree = list()  # type: _h_l_proc
	# avoiding duplicates:
	seen = set()  # type: _h_s_proc
	seen_add = seen.add
	root_processes = [
		x for x in root_processes
		if not (x in seen or seen_add(x))
	]
	if not root_processes:
		return

	cmd = ['taskkill']
	if force:
		cmd.append('/f')
	if tree:
		cmd.append('/t')
	for p in root_processes:
		if tree:
			whole_tree.extend([
				x for x in p.children(recursive=True)
				if not (x in seen or seen_add(x))
			])
		whole_tree.append(p)
		cmd.extend(['/pid', str(p.pid)])

	print (
		"Terminating {} with the command:\n{}".format(
			(
				'a "{}" process'.format(root_processes[0].name())
				if len(root_processes) == 1
				else 'processes ({})'.format(
					', '.join(x.name() for x in root_processes)
				)
			),
			' '.join(cmd)
		)
	)
	_call(cmd)

	gone, still_alive = psutil.wait_procs(
		whole_tree, timeout=timeout, callback=on_terminate
	)  # type: _h_l_proc
	if not still_alive:
		return

	print(
		'The "{}" process is still running. Force-killing it.'.format(still_alive[0].name())
		if len(still_alive) == 1
		else "Some processes are still running. Force-killing them:\n{}".format(
			', '.join(p.name() for p in still_alive)
		)
	)
	for p in still_alive:
		p.kill()


def __terminate_unix(
	root_processes,  # type: _h_l_proc
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_terminate=None  # type: _h_opt_call
):
	"""
	Low-level method to terminate a list of processes.

	:param root_processes: A process list to kill.
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	whole_tree = list()  # type: _h_l_proc
	# avoiding duplicates:
	seen = set()  # type: _h_s_proc
	seen_add = seen.add
	root_processes = [
		x for x in root_processes
		if not (x in seen or seen_add(x))
	]
	if not root_processes:
		return

	for p in root_processes:
		if tree:
			whole_tree.extend([
				x for x in p.children(recursive=True)
				if not (x in seen or seen_add(x))
			])
		whole_tree.append(p)

	print (
		'Terminating a "{}" process'.format(root_processes[0].name())
		if len(root_processes) == 1
		else 'Terminating processes ({})'.format(', '.join(
			x.name() for x in root_processes
		))
	)

	if not force:
		for p in whole_tree:
			p.terminate()
		gone, still_alive = psutil.wait_procs(
			whole_tree, timeout=timeout, callback=on_terminate
		)  # type: _h_l_proc
		if not still_alive:
			return
		print(
			'The "{}" process is still running. Force-killing it.'.format(still_alive[0].name())
			if len(still_alive) == 1
			else "Some processes are still running. Force-killing them:\n{}".format(
				', '.join(p.name() for p in still_alive)
			)
		)
		whole_tree = still_alive

	for p in whole_tree:
		p.kill()


__terminate_main = __terminate_windows if _pf.IS_WINDOWS else __terminate_unix


def __terminate_process_arg_cleanup(proc):
	if isinstance(proc, psutil.Process):
		return [proc]

	error = _err.WrongTypeError(proc, (psutil.Process, int), 'root_processes')

	if isinstance(proc, _str_t):
		raise error
	if isinstance(proc, int):
		return [psutil.Process(pid=proc)]
	try:
		proc = [x for x in proc]
	except TypeError:
		raise error
	res = list()  # type: _h_l_proc
	for p in proc:
		res.extend(__terminate_process_arg_cleanup(p))
	return res


def terminate(
	root_processes,  # type: _h_arg_proc
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_terminate=None  # type: _h_opt_call
):
	"""
	High-level platform-independent method to terminate a list of processes.

	:param root_processes:
		A process list to kill. One of:
		* `psutil.Process()` instance
		* int - the PID of a process
		* an iterable containing any of above
	:param tree: End the entire process tree, with all children.
	:param timeout:
		How long to wait for the process to finish (seconds), in graceful-kill mode.
	:param force:
		Instant-kill instead of graceful termination (waiting to end).
	:param on_terminate:
		A function which gets called when one of the processes being waited on
		is terminated and a `Process` instance is passed as callback argument.
	"""
	if not callable(on_terminate):
		on_terminate = None
	if not (isinstance(timeout, (int, float)) and timeout > 0):
		timeout = None

	__terminate_main(
		__terminate_process_arg_cleanup(root_processes),
		tree, timeout, force, on_terminate
	)


def __name_match_win(
	name,  # type: _str_h
	pattern  # type: _str_h
):
	name = name.replace('\\', '/')
	pattern = pattern.replace('\\', '/')
	return _fm.fnmatch(name, pattern)


_names_match = __name_match_win if _pf.IS_WINDOWS else _fm.fnmatchcase


def _pass(*args):
	return tuple(args)


def __terminate_by_proc_str(
	proc_str_f,  # type: _t.Callable[[psutil.Process], _str_h]
	proc_filters,  # type: _h_arg_nm
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_match=None,  # type: _h_opt_call
	on_terminate=None  # type: _h_opt_call
):
	"""
	A wrapper for terminating processes that match the given filters
	with some string generated from the process instance by the provided func.

	The given filters may contain either ints, instances of `psutil.Process()`
	or the actual string filters.
	"""
	if isinstance(proc_filters, _str_t):
		proc_filters = [proc_filters]
	try:
		proc_filters = [n for n in proc_filters]
	except TypeError:
		proc_filters = [proc_filters]
	if not proc_filters:
		return

	ints = [p for p in proc_filters if isinstance(p, int)]
	ints.extend([int(p) for p in proc_filters if isinstance(p, float)])
	ints.extend([p.pid for p in proc_filters if isinstance(p, psutil.Process)])
	ints = set(ints)
	str_names = [p for p in proc_filters if isinstance(p, _str_t)]

	def match_ints(
		process  # type: psutil.Process
	):
		return process.pid in ints

	def match_names(
		process  # type: psutil.Process
	):
		p_str = proc_str_f(process)
		return any(_names_match(p_str, x) for x in str_names)

	def match_both(
		process  # type: psutil.Process
	):
		return match_ints(process) or match_names(process)

	match = (
		match_both if str_names else match_ints
	) if ints else (
		match_names if str_names else None
	)

	if match is None:
		return

	def do_on_match(
		process  # type: psutil.Process
	):
		on_match(process)
		return process

	signal_match = do_on_match if callable(on_match) else _pass

	processes = [signal_match(p) for p in psutil.process_iter() if match(p)]
	terminate(processes, tree, timeout, force, on_terminate)


def _get_proc_name(
	proc  # type: psutil.Process
):
	return proc.name()


def _get_proc_path(
	proc  # type: psutil.Process
):
	return proc.exe()


def terminate_by_name(
	processes,  # type: _h_arg_nm
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_match=None,  # type: _h_opt_call
	on_terminate=None  # type: _h_opt_call
):
	"""
	Kill all the processes matching to the given filters by their name or PIDs.

	:param processes:
		Filename-filter(s). May contain:
			* string names, including wildcards ("tool*.exe")
			* PIDs
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
	__terminate_by_proc_str(
		_get_proc_name,
		processes, tree, timeout, force, on_match, on_terminate
	)


def terminate_by_path(
	processes,  # type: _t.Union[_str_h, _t.Iterable[_str_h]]
	tree=False,
	timeout=20,  # type: _h_timeout
	force=False,
	on_match=None,  # type: _h_opt_call
	on_terminate=None  # type: _h_opt_call
):
	"""
	Kill all the processes matching to the given filters by the full path.

	:param processes:
		Filename-filter(s). May contain:
			* string paths, including wildcards ("W:/tool*.exe")
			* PIDs
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
	__terminate_by_proc_str(
		_get_proc_path,
		processes, tree, timeout, force, on_match, on_terminate
	)
