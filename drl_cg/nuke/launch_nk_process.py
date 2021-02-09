"""
"""

__author__ = 'Lex Darlog (DRL)'

import os
import time
from PySide.QtCore import QProcess, QProcessEnvironment
from drl_common import filesystem as fs
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_h as _str_h,
	t_strict_str as _str,
	t_strict_unicode as _unicode,
)
from . import nk_envs


def launch_nuke_with_command(cmd='', home_override_env='DRL_NUKE_HOME'):
	if not isinstance(cmd, _str_t) or not cmd:
		cmd = '"%s"' % nk_envs.get_nuke_exe_path()

	# p = sp.Popen(cmd, stderr=None, stdin=None, stdout=None, shell=False)
	# p.wait()
	proc = QProcess()

	nuke_home_env = os.getenv(home_override_env, '')
	if nuke_home_env and os.path.exists(nuke_home_env) and os.path.isdir(nuke_home_env):
		curr_env = QProcessEnvironment(proc.processEnvironment())
		if curr_env.isEmpty():
			curr_env = QProcessEnvironment(QProcessEnvironment.systemEnvironment())
		curr_env.insert('HOME', nuke_home_env)
		proc.setProcessEnvironment(curr_env)

	def to_output():
		output = proc.readAll()
		if not isinstance(output, _str_t):
			try:
				output = _str(output)
			except:
				output = _unicode(output)
		output = output.strip()
		if output:
			print(output)

	proc.readyRead.connect(to_output)
	proc.start(cmd)
	proc.waitForFinished(-1)


def process(
		src_tex,
		out_tex='',
		remove_src_tex=False,
		nk_dir='',
		nk_script='',
		py_dir='',
		py_script='',
		nuke_dir='',
		nuke_exe='',
		auto_to_exr=True,
		home_override_env='DRL_NUKE_HOME',
		pre_wait=0.0,
		post_wait=3.0
):
		"""
		Produces Nuke's post-processing with a pre-defined nk script.

		:param src_tex: <string>, full path to baked EXR.
		:param out_tex:
			<string tuple of strings>, full path to resulting PNG.
			If omitted, a PNG file with the same basename is created.
		:param remove_src_tex:
			<bool>, whether to remove source EXR texture after processing.
		:param nk_script: optional path to a Nuke script file used to process the image.
		:param py_script: optional path to a python script launching render in Nuke.
		:param nuke_dir: optional path to the Nuke 8 folder.
		:param nuke_exe:
			Manually specify the exact filename (not path) of Nuke.exe or
			any bat/script file launching it and passing all the arguments.
		:param auto_to_exr:
			determines output file type when out texture is not provided manually
		:param home_override_env:
			the system variable, which, if set, will temporarily re-set HOME env.
		:return:
		"""
		from pprint import pprint as pp

		def wait_for(sec):
			if not isinstance(sec, (int, float)) or sec <= 0:
				return
			print('Waiting for {0} seconds...'.format(sec))
			time.sleep(sec)
		# src_tex = r'E:\1-Projects\5-ShaderFX\sources\Trash\Trash.exr'

		# print('Start error-handle arguments:')
		# pp([src_tex, out_tex, nk_dir, nk_script, py_dir, py_script, nuke_dir, nuke_exe])

		wait_for(pre_wait)

		src = nk_envs.get_src_tex(src_tex)
		out = nk_envs.get_out_tex(src_tex, out_tex, auto_to_exr)
		nuke_exe = nk_envs.get_nuke_exe_path(nuke_dir=nuke_dir, nuke_exe=nuke_exe)
		nk = nk_envs.get_nk_script_path(nk_dir=nk_dir, nk_filename=nk_script)
		py = nk_envs.get_py_script_path(py_dir=py_dir, py_filename=py_script)

		print('Finished error-handle arguments:')
		pp([nuke_exe, py, nk, src, out])

		fs.clean_path_for_file(out, overwrite_folders=1, remove_file=1)

		cmd = nk_envs.get_nuke_process_command(
			src, out,
			nuke_exe, py, nk,
			auto_to_exr=auto_to_exr
		)

		print("Launch Nuke with command: " + cmd)
		launch_nuke_with_command(cmd, home_override_env=home_override_env)

		wait_for(post_wait)
		if remove_src_tex:
			print("Removing raw rendered texture: " + src_tex)
			os.remove(src_tex)
		print("---- Nuke processing completed ----")
