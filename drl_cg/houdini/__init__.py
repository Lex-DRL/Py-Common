"""
Tools related to SideFX houdini.
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

from drl_cg.launcher import with_envs as _launch


def launch(
	hou_ver='17.5.229',
	redshift=False,
	*exe_args
):
	"""A wrapper to start a given Houdini version"""

	from . import env
	import drl_cg.redshift.env as rs_env
	envs = list()  # type: _t.List[_t.Tuple[_str_h, _t.Optional[_str_h]]]

	hou_install_path = env.hou_install_path(hou_ver)
	hou_exe = hou_install_path + env.EXE_SUBPATH

	if redshift and rs_env.INSTALL_PATH:
		envs.extend([
			('HOUDINI_DSO_ERROR', None),
			('HOUDINI_DSO_ERROR', 2),
			('PATH', rs_env.BIN_PATH),
			('HOUDINI_PATH', rs_env.hou_plugin_path(hou_ver))
		])

	cmd = [hou_exe]
	cmd.extend(exe_args)
	_launch(cmd, False, True, *envs)
