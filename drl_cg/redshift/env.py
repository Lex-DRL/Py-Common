"""
The following environment variables are supported, in fallback order:

	* DRL_REDSHIFT_INSTALL_PATH

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

import os as _os
import errno as _errno

from drl_cg.env import _clean


INSTALL_PATH = _clean(
	_os.environ.get('DRL_REDSHIFT_INSTALL_PATH', 'C:/ProgramData/Redshift'),
	is_dir=True
)
BIN_PATH = (INSTALL_PATH + '/bin') if INSTALL_PATH else ''


def hou_plugin_path(hou_ver='17.5.229'):
	hou_ver = hou_ver.replace('\\', '/').rstrip('/')

	if not hou_ver:
		raise OSError(_errno.ENOENT, "Houdini version not specified for RedShift")

	if not INSTALL_PATH:
		raise OSError(_errno.ENOENT, "RedShift install folder not found")

	path = '/'.join([
		INSTALL_PATH,
		'Plugins/Houdini',
		hou_ver.replace('\\', '/').strip('/')
	])
	path = _clean(path, is_dir=True, raise_error=True)

	return path
