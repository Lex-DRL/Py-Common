__author__ = 'DRL'


class NoPathError(ValueError):
	def __init__(self, object_name='', is_file=False, is_folder=True):
		fs_object = NoPathError.__get_fs_object_name(is_file, is_folder)

		if fs_object:
			msg = "No {0} path provided"
		else:
			msg = "No path provided"

		if object_name:
			msg += " for {1}."
		else:
			msg += "."

		msg = msg.format(fs_object, object_name)
		super(NoPathError, self).__init__(msg)

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
