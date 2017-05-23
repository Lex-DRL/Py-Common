__author__ = 'DRL'

import os

import drl_common.errors as err
from drl_common import filesystem as fs
from .processor import errors as _err


str_types = (str, unicode)

env_nuke_path = 'NUKE_LOCATION'
env_nuke_exe = 'NUKE_EXE_NAME'
env_py_dir = 'DRL_BK_PY_DIR'
env_nk_dir = 'DRL_BK_NK_DIR'

default_py_dir = r'S:\0-Settings\Python\for_nuke'
default_py_script = r'process_with_script.py'
default_nk_dir = r'S:\0-Settings\Python\for_nuke'
default_nk_script = r'post-bake_turtle_unity.nk'
default_nuke_dir = r'C:\Program Files\Nuke8.0v5'
default_nuke_exe = 'Nuke8.0.exe'


def get_nuke_exe_path(full_path='', nuke_dir='', nuke_exe=''):
	if isinstance(full_path, str_types) and full_path:
		fs.error_if.not_existing_file(full_path)
		return full_path.replace('/', '\\')

	if not (isinstance(nuke_dir, str_types) and nuke_dir):
		nuke_dir = os.getenv(env_nuke_path, default_nuke_dir)
	fs.error_if.not_existing_dir(nuke_dir)

	if not (isinstance(nuke_exe, str_types) and nuke_exe):
		nuke_exe = os.getenv(env_nuke_exe, default_nuke_exe)
	err.NotStringError(nuke_exe, 'nuke_exe').raise_if_needed()
	nuke_exe = os.path.join(nuke_dir, nuke_exe).replace('/', '\\')
	fs.error_if.not_existing_file(nuke_exe)
	return nuke_exe


def __do_return_full_path(full_path, check_f=None):
	if check_f is None:
		check_f = fs.error_if.path_not_readable
	if isinstance(full_path, str_types):
		full_path = full_path.replace('/', '\\')
		if '\\' in full_path:
			check_f(full_path)
			return True, full_path
	return False, full_path


def get_nk_script_path(full_path='', nk_dir='', nk_filename=''):
	is_abs, full_path = __do_return_full_path(full_path)
	if is_abs:
		return full_path.replace('\\', '/')

	is_abs, nk_filename = __do_return_full_path(nk_filename)
	if is_abs:
		return nk_filename.replace('\\', '/')

	if not (isinstance(nk_dir, str_types) and nk_dir):
		nk_dir = os.getenv(env_nk_dir, default_nk_dir)
	fs.error_if.not_existing_dir(nk_dir)

	if not (isinstance(nk_filename, str_types) and nk_filename):
		nk_filename = default_nk_script
	nk_filename = os.path.join(nk_dir, nk_filename).replace('\\', '/')
	fs.error_if.path_not_readable(nk_filename)
	return nk_filename


def get_py_script_path(full_path='', py_dir='', py_filename=''):
	is_abs, full_path = __do_return_full_path(full_path)
	if is_abs:
		return full_path

	is_abs, py_filename = __do_return_full_path(py_filename)
	if is_abs:
		return py_filename

	if not (isinstance(py_dir, str_types) and py_dir):
		py_dir = os.getenv(env_py_dir, default_py_dir)
	fs.error_if.not_existing_dir(py_dir)

	if not (isinstance(py_filename, str_types) and py_filename):
		py_filename = default_py_script
	py_filename = os.path.join(py_dir, py_filename).replace('/', '\\')
	fs.error_if.path_not_readable(py_filename)
	return py_filename


def get_src_tex(src_tex):
	if not src_tex:
		raise _err.NoPathError('source texture')
	if isinstance(src_tex, (str, unicode)):
		fs.error_if.path_not_readable(src_tex)
		return src_tex.replace('\\', '/')
	fs.error_if.path_not_readable(src_tex)
	return src_tex.replace('\\', '/')


def get_out_tex(src_tex, out_tex='', auto_to_exr=True):
	if not out_tex:
		out_tex = os.path.splitext(src_tex)[0] + (
			'_.exr' if auto_to_exr else '.png'
		)
	err.NotStringError(out_tex, 'out_tex').raise_if_needed()
	return out_tex.replace('\\', '/')


def get_nuke_process_command(
	src, out, nuke_exe='', py='', nk='', nuke_x=False, auto_to_exr=True
):
	src = get_src_tex(src)
	out = get_out_tex(src, out, auto_to_exr)
	nuke_exe = get_nuke_exe_path(nuke_exe)
	py = get_py_script_path(py)
	nk = get_nk_script_path(nk)

	return '"{nuke}" {nukex} -t "{py}" "{nk}" "{src}" "{out}"'.format(
		nuke=nuke_exe,
		nukex='--nukex' if nuke_x else '',
		py=py,
		nk=nk,
		src=src,
		out=out
	)
