__author__ = 'DRL'

import os, errno, platform


env_lib = 'VTF_LIB_DIR'
env_exe = 'VTF_CMD_EXE'
def_exe = 'VTFCmd.exe'


def exe_path():
	"""
	Get the path to the VTFCmd executable. Also an error may be thrown
	if the necessary environment variables are not defined or the given path
	cannot be executed
	"""
	path = os.getenv(env_lib)
	if (path is None) or not path:
		raise OSError(errno.EFAULT, '"%s" environment variable is undefined' % env_lib)
	path = path.replace('\\', '/').rstrip('/')
	exe = os.getenv(env_exe, def_exe)
	if not exe:
		raise OSError(errno.ENOENT, 'No exe file specified (try setting "%s" environment variable)' % env_exe)
	exe = exe.replace('\\', '/').strip('/')
	path = '/'.join((path, exe))
	path = os.path.abspath(path)  # since now we may need windows-style slashes for errors
	if 'windows' in platform.system().lower() and not path.lower().endswith('.exe'):
		path += '.exe'
	if not os.path.exists(path):
		raise OSError(errno.ENOENT, "VTFCmd doesn't exist at the given path: " + path)
	if not os.path.isfile(path):
		raise OSError(errno.EISDIR, "VTFCmd path points to a directory, not a file: " + path)
	if not os.access(path, os.X_OK):
		raise OSError(errno.EACCES, "The file at the given path is not executable: " + path)
	return path

def decompile_single(src_file, dest=''):
	pass