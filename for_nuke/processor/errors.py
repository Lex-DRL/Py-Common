__author__ = 'DRL'


class _NukePathBaseError(ValueError):
	def __init__(
		self, object_name='',
		is_file=False, is_folder=True,
		msg_prefix_with_type="No {0} path provided",
		msg_prefix_no_type="No path provided",
		msg_suffix=""
	):
		fs_object = _NukePathBaseError.__get_fs_object_name(is_file, is_folder)

		if fs_object:
			msg = msg_prefix_with_type
		else:
			msg = msg_prefix_no_type

		if object_name:
			msg += " for {1}."
		else:
			msg += "."

		if msg_suffix:
			msg += msg_suffix

		msg = msg.format(fs_object, object_name)
		super(_NukePathBaseError, self).__init__(msg)

		self.object_name = object_name
		self.is_file = is_file
		self.is_folder = is_folder

	@staticmethod
	def __get_fs_object_name(is_file=False, is_folder=True):
		if is_file and is_folder:
			return 'file/folder'
		if not(is_file or is_folder):
			return ''
		if is_file:
			return 'file'
		return 'folder'


class NoPathError(_NukePathBaseError):
	def __init__(self, object_name='', is_file=False, is_folder=True, msg_suffix=None):
		super(NoPathError, self).__init__(
			object_name, is_file, is_folder, msg_suffix=msg_suffix
		)


class WrongPathError(_NukePathBaseError):
	def __init__(self, object_name='', is_file=False, is_folder=True, msg_suffix=None):
		super(WrongPathError, self).__init__(
			object_name, is_file, is_folder,
			"Wrong {0} path provided",
			"Wrong path provided",
			msg_suffix
		)



nuke_dir = NoPathError('NUKE directory')
nuke_exe = NoPathError('NUKE .exe', is_file=True)

nk_dir = NoPathError('nk-script directory')
nk_file = NoPathError('nk-script', is_file=True)

py_dir = NoPathError('python script directory')
py_file = NoPathError('python script', is_file=True)

nuke_exe_with_quotes = WrongPathError(
	'nuke.exe', is_file=True, msg_suffix=' It contains quote character(s).'
)

py_file_with_quotes = WrongPathError(
	'python script', is_file=True, msg_suffix=' It contains quote character(s).'
)

nk_file_with_quotes = WrongPathError(
	'nk-script', is_file=True, msg_suffix=' It contains quote character(s).'
)