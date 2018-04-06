__author__ = 'DRL'

import os
import shutil as sh

import drl_common.errors as err
from drl_common import utils
from . import errors, error_if, file_time
from .. import is_maya as _im


_is_maya = _im.is_maya()
if _is_maya:
	from maya import cmds


class FileFilter(object):
	"""
	Class that formats file-filter string in the common way.

	To get the formatted version, just use str() on the instance.

	:param name: <str> User-friendly filter description.
	:param filters: <tuple of strings> File masks (like: '*.ma')
	"""
	def __init__(self, name, filters=None):
		super(FileFilter, self).__init__()
		self.__name = ''
		self.__filters = tuple()
		self._set_name(name)
		self._set_filters(filters)

	__error_check_conditions = [
		lambda x: isinstance(x, FileFilter),
		lambda x: not x,
		lambda x: isinstance(x, (str, unicode)),
		lambda x: isinstance(x, (list, tuple)) and all(
			[isinstance(f, (str, unicode)) for f in x]
		)
	]

	@staticmethod
	def error_check_condition(x):
		cond = FileFilter.__error_check_conditions[x]
		assert callable(cond)
		return cond

	@staticmethod
	def error_check_will_succeed(file_filter):
		return any([c(file_filter) for c in FileFilter.__error_check_conditions])

	@staticmethod
	def error_check_as_argument(file_filter, arg_name=None):
		"""
		Ensures the given argument is FileFilter.

		If it is, just returns the same instance.

		If not, tries to create a new one:

		* not(file_filter) - jut default "All Files"
		* string - all files, with the given nice name
		* list/tuple of strings:
			* 1 item - same as string
			* 2 or more items - the 1st string is a name, the others are filters.

		:param file_filter: the argument itself
		:param arg_name: <optional str> name of the argument (for proper error message).
		:return: <FileFilter>
		"""
		conditions = FileFilter.__error_check_conditions
		if conditions[0](file_filter):
			# it's FileFilter
			return file_filter
		if conditions[1](file_filter):
			# it's empty / None / not True
			return FileFilter('All Files')
		if conditions[2](file_filter):
			# single string
			return FileFilter(file_filter)
		if conditions[3](file_filter):
			# list/tuple of strings
			num = len(file_filter)
			if num == 1:
				return FileFilter(file_filter[0])
			elif num == 2:
				return FileFilter(*file_filter)
			else:
				return FileFilter(file_filter[0], file_filter[1:])
		raise err.WrongTypeError(file_filter, FileFilter, arg_name)

	def _set_name(self, name):
		if not name:
			name = ''
		self.__name = err.NotStringError(name, 'name').raise_if_needed()

	def set_name(self, name):
		self._set_name(name)
		return self

	@property
	def name(self):
		return self.__name

	@name.setter
	def name(self, value):
		self._set_name(value)

	@staticmethod
	def _error_check_filters_as_list(filters):
		"""
		Performs error-check for <filters> argument.

		WARNING! The result is list. It's your responsibility to convert it back to tuple.

		Check for duplicates is not performed. It's up you you, too.
		"""
		if filters is None or not filters:
			filters = ['']
		if isinstance(filters, (str, unicode)):
			filters = [filters]
		if isinstance(filters, tuple):
			filters = list(filters)
		filters = err.WrongTypeError(
			filters, list, 'filters', 'tuple/list'
		).raise_if_needed()
		# assert isinstance(filters, list)
		# filters = ['*.*', '*.ma']
		for i, f in enumerate(filters):
			if not f:
				filters[i] = '*.*'
				continue
			err.NotStringError(f, 'filter #' + str(i)).raise_if_needed()
		return filters

	def _set_filters(self, filters):
		filters = FileFilter._error_check_filters_as_list(filters)
		self.__filters = tuple(utils.remove_duplicates(filters))

	def set_filters(self, filters):
		self._set_filters(filters)
		return self

	def append_filters(self, filters):
		filters_nu = list(self.__filters)
		filters_nu.extend(FileFilter._error_check_filters_as_list(filters))
		self.__filters = tuple(utils.remove_duplicates(filters_nu))
		return self

	@property
	def filters(self):
		return self.__filters[:]

	@filters.setter
	def filters(self, value):
		self._set_filters(value)

	def as_string(self):
		filters = ' '.join(self.__filters)
		name = self.__name
		joined_list = [name] if name else list()
		joined_list.append('(%s)' % filters)
		return ' '.join(joined_list)

	def __repr__(self):
		return "< %s('%s', %s) class instance >" % (self.__class__.__name__, self.__name, self.__filters)

	def __str__(self):
		return self.as_string()


def __convert_path_slashes(path, wrong_slash='\\', right_slash='/', trailing_slash=None, leading_slash=0):
	err.NotStringError(path, 'path').raise_if_needed()
	if not path:
		return ''

	assert isinstance(path, (str, unicode))
	path = path.replace(wrong_slash, right_slash)
	if not (trailing_slash is None):
		path = path.rstrip(right_slash)
		if trailing_slash:
			path += right_slash
	if not (leading_slash is None):
		path = path.lstrip(right_slash)
		if leading_slash:
			path = right_slash + path
	return path


def to_windows_path(path, trailing_slash=None, leading_slash=False):
	"""
	Ensures given path has Windows-style slashes. ("/" -> "\")

	:type path: str|unicode
	:param trailing_slash:
		Whether we need to ensure path has or lacks trailing slash:
			* None: (default) no check performed. Leave as is, just replace path slashes.
			* 0/False: Force-remove trailing slash
			* 1/True: Force-leave (single) trailing slash.
	:type trailing_slash: bool|None
	:param leading_slash:
		The same for leading slash. However, it's <0> (force-removed) by default.
	:type leading_slash: bool|None
	:rtype: str|unicode
	"""
	return __convert_path_slashes(path, '/', '\\', trailing_slash, leading_slash)


def to_unix_path(path, trailing_slash=None, leading_slash=0):
	"""
	Ensures given path has unix-style slashes. ("\" -> "/")

	:type path: str|unicode
	:param trailing_slash:
		Whether we need to ensure path has or lacks trailing slash:
			*
				None: (default) no check performed.
				Leave as is, just replace path slashes.
			* False: Force-remove trailing slash
			* True: Force-leave (single) trailing slash.
	:type trailing_slash: bool|None
	:param leading_slash:
		The same for leading slash.
		However, it's <0> (force-removed) by default.
	:type leading_slash: bool|None
	:rtype: str|unicode
	"""
	return __convert_path_slashes(
		path,
		trailing_slash=trailing_slash,
		leading_slash=leading_slash
	)


def __is_overwrite_enabled(
	overwrite, path,
	yes_button='Yes', no_button='No (error)',
	message='''You're trying to access a file as a folder.
Replace file with an empty folder?
{0}''',
	annotation_yes='The file will be removed and a folder at the same path will be created',
	annotation_no='Unable to continue, the error will be thrown',
	icon='warning'
):
	"""
	Determine whether we're allowed to overwrite a file/folder.

	:param overwrite:
		What to do if we face a case where we need to overwrite a file/folder.
			* 0/False: Nothing. Error is thrown.
			* 1/True: Overwrite.
			*
				2 or more when called from Maya:
				display interactive dialog allowing a user to choose.
				When called outside of Maya, considered as <True>.
	:type overwrite: int|bool
	:type path: str|unicode
	"""
	if _is_maya and overwrite > 1:
		user_choice = cmds.confirmDialog(
			title='Overwrite warning',
			message=message.format(path),
			messageAlign='left',
			button=[yes_button, no_button],
			annotation=[annotation_yes, annotation_no],
			defaultButton=yes_button,
			cancelButton=no_button,
			dismissString=no_button,
			icon=icon
		)
		return user_choice == yes_button
	if overwrite:
		return True
	return False


def ensure_breadcrumbs_are_folders(path, overwrite=0):
	"""
	All the parent folders of the given filesystem object (a file / child folder)
	are recursively checked whether they are actually folders.

	If they don't exist, they're created.
	If any of parents is actually a file itself, either it's removed or an error is thrown.

	:param path: File path (absolute recommended).
	:type path: str|unicode
	:param overwrite:
		What to do if a parent folder is actually a file itself:
			* 0/False: Nothing. Error is thrown.
			* 1/True: Remove file and create folder with it's name.
			*
				2 or more when called from Maya:
				display interactive dialog allowing a user to choose.
				When called outside of Maya, considered as <True>.
	:return:
		Cleaned-up path on success.
		I.e., unix-style slashes, removed extra trailing/leading slashes.
	:rtype: str|unicode
	:raises:
		* NotStringError - path isn't a string at all
		* EmptyStringError - path is empty
		* NoFileOrDirError - the path starts with a disk which doesn't exist.
		* UnknownObjectError - any of breadcrumbs is not a folder nor a file.
		* ParentFolderIsFileError - a breadcrumb is a file, and overwrite is disabled.
	"""
	# path = r'e:\1-Projects\0-Common_Code\qqq\\'
	path = to_unix_path(path, trailing_slash=0)
	err.NotStringError(path, 'path').raise_if_needed_or_empty()
	if not path.rstrip('/'):
		return path

	checked = ''
	path_for_split = path
	if path.startswith('/'):
		path_for_split = path.lstrip('/')
		path = '/' + path_for_split
		checked = '/'
	breadcrumbs = path_for_split.split('/')

	if len(breadcrumbs) < 2:
		return path
	del path_for_split

	breadcrumbs = breadcrumbs[:-1]
	checked += breadcrumbs.pop(0)
	if checked.endswith(':') and not os.path.exists(checked):
		raise errors.NoFileOrDirError(checked, "No such disk found in system")

	# we're sure at least the disk exists

	def __check_item(item):
		"""
		Handle single breadcrumb item (aka path element / parent folder).
		Check if it's a valid folder. And if not:

		* try to create it if path is available
		* try to remove file at this path and replace with a folder (if allowed)
		"""
		if not os.path.exists(item):
			os.makedirs(item)
			return
		#path already exist:

		if os.path.isdir(item):
			return
		if not os.path.isfile(item):
			raise errors.UnknownObjectError(item)
		# we're facing a file (not a dir):

		if __is_overwrite_enabled(overwrite, item):
			os.remove(item)
			os.makedirs(item)
			return
		raise errors.ParentFolderIsFileError(path, item, overwrite)

	__check_item(checked)  # we already have the beginning to check
	while breadcrumbs:
		__check_item(checked)
		checked += '/' + breadcrumbs.pop(0)

	return path


def clean_path_for_folder(path, overwrite=0):
	"""
	Creates the given folder path. Creates intermediate directories if needed.

	:param path:
		Folder path. Any slashes. Doesn't matter if there's trail-slash.
	:type path: str|unicode
	:param overwrite:
		What to do if a parent folder is actually a file itself:
			* 0/False: Nothing. Error is thrown.
			* 1/True: Remove file and create folder with it's name.
			*
				2 or more when called from Maya:
				display interactive dialog allowing a user to choose.
				When called outside of Maya, considered as <True>.
	:return:
		Cleaned-up path on success.
		I.e., unix-style slashes, removed extra trailing/leading slashes.
	:rtype: str|unicode
	"""
	path = ensure_breadcrumbs_are_folders(path, overwrite)
	# it's guaranteed to have no trailing slash now

	if not os.path.exists(path):
		if __is_overwrite_enabled(
			overwrite, path, no_button='No',
			message="Folder doesn't exist. Create?\n{0}",
			annotation_yes='Create the folder at the given path',
			annotation_no="Don't create it",
			icon='question'
		):
			os.makedirs(path)
		return path

	if os.path.isdir(path):
		return path

	if not os.path.isfile(path):
		raise errors.UnknownObjectError(path)

	if __is_overwrite_enabled(overwrite, path):
		os.remove(path)
		os.makedirs(path)
		return path

	raise errors.FileAlreadyExistError(path, overwrite)


def clean_path_for_file(path, overwrite_folders=0, remove_file=0):
	"""
	Prepares the path for a file. I.e.:
		* creates parent directories
		* removes the existing file if needed

	:param path: Folder path. Any slashes. Doesn't matter if there's trail-slash.
	:type path: str|unicode
	:param overwrite_folders:
		What to do if a parent folder is actually a file itself:
			* 0/False: Nothing. Error is thrown.
			* 1/True: Remove file and create folder with it's name.
			* 2 or more when called from Maya: display interactive dialog allowing a user to choose. When called outside of Maya, considered as <True>.
	:return:
		Cleaned-up path on success.
		I.e., unix-style slashes, removed extra trailing/leading slashes.
	:rtype: str|unicode
	"""
	path = ensure_breadcrumbs_are_folders(path, overwrite_folders)
	# it's guaranteed to have no trailing slash now

	if not os.path.exists(path):
		return path

	if os.path.isfile(path):
		if __is_overwrite_enabled(
			remove_file, path, no_button='No',
			message='File already exist. Overwrite it (remove)?\n{0}',
			annotation_yes='Remove the file',
			annotation_no='Keep the file'
		):
			os.remove(path)
		return path

	if os.path.isdir(path):
		if __is_overwrite_enabled(
			remove_file, path,
			message='Folder already exist at the same path as the file. Remove it?\n{0}',
			annotation_yes="Remove the folder with all of it's contents",
			annotation_no='Keep the folder (error is thrown)',
			icon='critical'
		):
			sh.rmtree(path)
			return path
		raise errors.FileAlreadyExistError(path, overwrite_folders, 'Folder already exist at the file path')

	raise errors.UnknownObjectError(path)


# ---------------------------------------------------------

# OLD:

# def clean_path_for(path='', tofile=False, tofolder=False, force_file_delete=False):
#	"""
#	This function forces the specified path to become either file or folder,
#	depending on which option is selected ('tofile' or 'tofolder' parameters set to True).
#	If the specified path is already object of a specified type or a link to it, nothing happens.
#	If not, the path is cleared for file creation (in file mode) or replaced with the folder.
#	"""
#	if path == '':
#		msg = "\nThe path isn't specified."
#		wrn.warn(msg, RuntimeWarning, stacklevel=2)
#		return
#	if not (tofile or tofolder):
#		msg = '\nNot "isfile" nor "isfolder" parameter set as True in the call for the clean_path_for function.'
#		wrn.warn(msg, RuntimeWarning, stacklevel=2)
#		return
#
#	# <tofolder> mode
# 	if tofolder:
# 		if os.path.isfile(path) and not os.path.isdir(path):
# 			os.remove(path)
# 		if not os.path.isdir(path):
# 			os.makedirs(path)
# 		return
#
# 	# now we're guaranteed in <tofile> mode
# 	if os.path.isdir(path):
# 		if os.path.islink(path):
# 			os.remove(path)
# 		else:
# 			sh.rmtree(path)
# 	elif os.path.isfile(path) and force_file_delete:
# 		os.remove(path)
# 	# make sure full parent directories path is created:
# 	root_path = os.path.split(path)[0]
# 	if root_path:
# 		clean_path_for(root_path, tofolder=True)


# path = r'E:\1-Projects\Maya\ssTrapsSrc\3delight\_ToRender\textures'
def empty_dir(path, overwrite=0):
	path = clean_path_for_folder(path, overwrite)
	if not os.path.exists(path):
		os.makedirs(path)

	files = os.listdir(path)
	for f in files:
		# f = files[0]
		filepath = os.path.join(path, f)
		if os.path.isdir(filepath) and not os.path.islink(filepath):
			sh.rmtree(filepath)
		else:
			os.remove(filepath)


def do_with_file(path, function, mode='r', opening_function=None):
	"""
	Performs something with a file at the given path with the given function.
	Also performs the checks to make sure file is accessable.

	:param path: string path to a file
	:param function: function taking exactly 1 argument (the opened file)
	:param mode: the mode of how file should be opened
	:param opening_function: extra-function defining the way to perform the actual
		open() command. This function takes exactly 2 arguments.
	:return: the result of the given function's execution
	"""
	def check_func_arg(func, number_of_arguments):
		import inspect
		if not hasattr(func, '__call__'):
			raise Exception('Function expected. Got: ' + repr(func))

		num_args = len(inspect.getargspec(func).args)
		if num_args != number_of_arguments:
			raise Exception(
				"Provided function has wrong number of arguments. Expected 1, got: " +
				str(num_args)
			)

	check_func_arg(function, 1)
	if opening_function is None:
		if 'r' in mode:
			error_if.path_not_readable(path)
		if 'w' in mode or 'a' in mode or '+' in mode:
			error_if.path_not_writeable(path)
		opening_function = lambda p, m: open(p, m)
	else:
		check_func_arg(opening_function, 2)

	try:
		with opening_function(path, mode) as fl:
			# fl = open(path)
			res = function(fl)
	except IOError as e:
		raise Exception('Error reading file "{0}":\n{1}'.format(path, e))
	return res


def read_file_lines(path, strip_newline_character=True):
	"""
	High-level function for reading file contents as list of lines.
	Automatically detects file encoding and handles it (including utf-8).

	:type path: str|unicode
	:param strip_newline_character:
		Whether to remove trailing newline character at each line
	:rtype: list[str|unicode]
	"""
	import codecs
	import chardet
	# path = r'e:\1-Projects\0-Common_Code\Sources\Unity\DRL\Shaders\AIVIK-U5\Y-Fog\Volumetric\tmp.txt'
	# path = r'e:\1-Projects\0-Common_Code\Sources\Unity\DRL\Shaders\AIVIK-U5\Y-Fog\Volumetric\MultiTex-Diffuse-x4-gen.shader'

	# get encoding:
	fl_bytes = min(32, os.path.getsize(path))
	raw = do_with_file(path, lambda x: x.read(fl_bytes), 'rb')
	if raw.startswith(codecs.BOM_UTF8):
		encoding = 'utf-8-sig'
	else:
		encoding = chardet.detect(raw)['encoding']

	read_args = [
		path,
		lambda f: f.readlines(),
	]
	if not encoding.startswith('ascii'):
		read_args += [
			'rb',
			lambda p, m: codecs.open(p, m, encoding=encoding)
		]
	lines = do_with_file(*read_args)

	if strip_newline_character:
		lines = [l.rstrip('\n') for l in lines]

	return lines
