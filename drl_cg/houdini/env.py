"""
The following environment variables are supported, in fallback order:

	* DRL_HOU_INSTALL_PATH_<version>
	* DRL_HOU_INSTALL_PATH
	* DRL_HOU_INSTALLS_PATH + /<version>
	* DRL_CG_PATH + /Houdini/<version>
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
	str_hint as _str_h,
)

# endregion

import os as _os
from os import path as _pth
import errno as _errno

from drl_cg.env import (
	_clean,
	DRL_CG_PATH as _CG_PATH,
)


HOU_INSTALLS_PATH = _clean(
	_os.environ.get(
		'DRL_HOU_INSTALLS_PATH',
		(_CG_PATH + '/Houdini') if _CG_PATH else ''
	),
	is_dir=True
)
EXE_SUBPATH = '/bin/houdini.exe'


def hou_install_path(hou_ver='17.5.229'):
	"""
	Finds an existing Houdini install dir by following this fallback chain,
	ensuring the path is actually a folder:

		* 'DRL_HOU_INSTALL_PATH_<hou_ver>' env-var
		* 'DRL_HOU_INSTALL_PATH' env-var
		* <hou_ver> in DRL_HOU_INSTALLS_PATH

	If no match is found, throws an error.

	:return: A path to the houdini-install base dir.
	"""
	environ = _os.environ

	def try_from_env(env_nm):
		"""
		Try to find a houdini path from a given env-var,
		making sure the dir actually exist.
		"""
		from_env = _clean(environ.get(env_nm))
		if from_env:
			if _pth.isdir(from_env) and _pth.isfile(from_env + EXE_SUBPATH):
				return from_env
			print(
				"'{}' env-var is set but doesn't point to a Houdini dir. Proceeding.".format(env_nm)
			)
		return ''

	hou_ver = _clean(hou_ver)
	if hou_ver:
		override = try_from_env('DRL_HOU_INSTALL_PATH_' + hou_ver)
		if override:
			return override
	else:
		override = try_from_env('DRL_HOU_INSTALL_PATH')
		if override:
			return override

	# an env-var for the explicit version is not found

	if not HOU_INSTALLS_PATH:
		if hou_ver:
			raise OSError(_errno.ENOENT, "No Houdini installation variable is set")

		# try to find the latest version specified with env:
		install_envs = [
			(k.upper(), _clean(v, is_dir=True))
			for k, v in environ.items() if (
				isinstance(k, _str_t) and k.upper().startswith('DRL_HOU_INSTALL_PATH')
			)
		]
		if not install_envs:
			raise OSError(_errno.ENOENT, "No Houdini installation variable is set")

		proper_envs = {
			k: v
			for k, v in install_envs if (
				v and _pth.isfile(v + EXE_SUBPATH)
			)
		}  # type: _t.Dict[str, _str_h]
		if not proper_envs:
			raise OSError(
				_errno.ENOENT,
				"The following Houdini installation variables are set but none of them "
				"contain the actual Houdini install:\n" +
				'\t'.join(zip(*install_envs)[0])
			)

		if 'DRL_HOU_INSTALL_PATH' in proper_envs.keys():
			return proper_envs['DRL_HOU_INSTALL_PATH']
		latest_ver = sorted(proper_envs.keys())[-1]
		return proper_envs[latest_ver]

	# HOU_INSTALLS_PATH is specified

	if hou_ver:
		# try to find at the default path:
		hou_install = _clean(
			HOU_INSTALLS_PATH + '/' + hou_ver,
			is_dir=True,
			raise_error=True
		)
		if not _pth.isfile(hou_install + EXE_SUBPATH):
			raise OSError(_errno.ENOENT, "The path isn't a Houdini folder", hou_install)
		return hou_install

	# HOU_INSTALLS_PATH is specified but hou_ver is not

	# try to use the HOU_INSTALLS_PATH as the actual houdini folder:
	if _clean(
		HOU_INSTALLS_PATH + EXE_SUBPATH,
		is_file=True
	):
		# yes, it's the only Houdini install indeed
		return HOU_INSTALLS_PATH

	# try to find the latest houdini install if HOU_INSTALLS_PATH has any:

	# all the following lists contain full paths:
	dir_contents = [
		_clean(HOU_INSTALLS_PATH + '/' + p)
		for p in _os.listdir(HOU_INSTALLS_PATH)
	]
	subdirs = [p for p in dir_contents if _pth.isdir(p)]
	hou_installs = [
		p for p in subdirs
		if _clean(p + EXE_SUBPATH, is_file=True)
	]
	if not hou_installs:
		raise OSError(_errno.ENOENT, "No Houdini installations can be found")
	return sorted(hou_installs)[-1]
