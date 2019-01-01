__author__ = 'DRL'

try:
	# support type hints:
	from typing import *
	unicode = str  # fix errors in Python 3
except ImportError:
	pass

import os
from os import path as _pth
import shutil as sh

import drl_common.errors as err
from drl_common import utils
from . import errors, error_if, file_time
from .. import is_maya as _im
from modules import pip_install as _inst


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
	return bool(overwrite)


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
	:param remove_file:
		Whether to automatically remove a file at the given path:
			* 0/False: Nothing. Error is thrown.
			* 1/True: Overwrite.
			*
				2 or more when called from Maya:
				display interactive dialog allowing a user to choose.
				When called outside of Maya, considered as <True>.
	:type remove_file: int|bool
	:return:
		3 results:
			*
				Cleaned-up path on success.
				I.e., unix-style slashes, removed extra trailing/leading slashes.
			* Whether the path was cleaned-up (removed folder/file at this path)
			*
				Whether interactive dialog was shown to a user
				**AND** they have chosen to cancel overwrite process
				(i.e., path was **not** cleaned).
	"""
	path = ensure_breadcrumbs_are_folders(
		path, overwrite_folders
	)  # type: Union(str, unicode)
	# it's guaranteed to have no trailing slash now

	if not os.path.exists(path):
		return path, False, False

	if os.path.isfile(path):
		overwritten = __is_overwrite_enabled(
			remove_file, path, no_button='No',
			message='File already exist. Overwrite it (remove)?\n{0}',
			annotation_yes='Remove the file',
			annotation_no='Keep the file'
		)
		if overwritten:
			os.remove(path)
		user_cancelled = remove_file > 1 and not overwritten
		return path, overwritten, user_cancelled

	if os.path.isdir(path):
		overwritten = __is_overwrite_enabled(
			remove_file, path,
			message='Folder already exist at the same path as the file. Remove it?\n{0}',
			annotation_yes="Remove the folder with all of it's contents",
			annotation_no='Keep the folder (error is thrown)',
			icon='critical'
		)
		user_cancelled = remove_file > 1 and not overwritten
		if overwritten:
			sh.rmtree(path)
			return path, overwritten, user_cancelled
		raise errors.FileAlreadyExistError(path, overwrite_folders, 'Folder already exist at the file path')

	raise errors.UnknownObjectError(path)

# ---------------------------------------------------------


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


def detect_file_encoding(
	file_path,  # type: Union[str, unicode]
	limit=64*1024,  # 64 Kb
	mode=4
):
	"""

	:param file_path:
	:param limit: max amount of bytes read from the file. If non-int or 0 and less, read it entirely .
	:param mode:
		In all modes, we try to find a BOM first. If it's found, detect the corresponding UTF-X encoding from it.
		Otherwise, proceed to the trial-and-error-based detection:

		*
			0 - don't use any external modules.
			`ascii` or `utf-8` (with 1.0 precision) if any detected,
			the default system's codepage (with 0.0 precision) otherwise.
		* 1 - use `chardet` only
		* 2 - use `chardet` **WITH** `UnicodeDammit` from `beautifulsoup4`.
		*
			3 and 4:

			First, try without external modules. If no success, try with them:

			`chardet`-only or `chardet` + `UnicodeDammit`, respectively.
	:return:
		* `str` detected encoding
		* `float` how sure the detector is:
			* in no-modules mode, 1.0 on success, 0.0 if default returned
			* in chardet-mode, the actual 'sureness' of detector
			* in UnicodeDammit-mode, always excactly 0.5
	"""
	# file_path = r'p:\0-Unity\builtin_shaders\CGIncludes\AutoLight.cginc'
	import codecs

	# first, try to detect BOM.
	# an extension of: https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
	first_bytes = min(32, _pth.getsize(file_path))  # int for now
	with open(file_path, 'rb') as fl_first:
		first_bytes = fl_first.read(first_bytes)  # str now
	for bom, enc in (
		(codecs.BOM_UTF32_BE, 'utf-32-be'),
		(codecs.BOM_UTF32_LE, 'utf-32-le'),
		(codecs.BOM_UTF8, 'utf-8-sig'),
		(codecs.BOM_UTF16_BE, 'utf-16-be'),
		(codecs.BOM_UTF16_LE, 'utf-16-le'),
	):
		if first_bytes.startswith(bom):
			return enc, 1.0
	del first_bytes

	if isinstance(mode, float):
		mode = int(mode)
	if not isinstance(mode, int):
		try:
			mode = int(mode)
		except:
			mode = int(bool(mode))
	if mode < 1:
		mode = 0

	if not (isinstance(limit, int) and limit > 0):
		limit = None

	raw = ''
	with open(file_path, 'rb') as fl:
		raw = fl.read() if limit is None else fl.read(limit)

	def _mode_no_modules(bytes_string):
		"""
		The simplest mode.
		It has no dependencies on external modules, but can only differentiate
		ascii from UTF and assumes the default codepage if neither of those is detected.

		Based on: https://unicodebook.readthedocs.io/guess_encoding.html
		"""
		def is_ascii():
			try:
				# print(raw.decode('koi8-r')[1181:1230])
				# print(raw.decode('cp1252')[1181:1230])
				# print(raw.decode('ascii')[1181:1230])
				bytes_string.decode('ascii')
			except UnicodeDecodeError:
				return False
			else:
				return True

		def is_utf8_strict():
			try:
				# print(raw.decode('koi8-r')[1181:1230])
				# print(raw.decode('cp1252')[1181:1230])
				# print(raw.decode('ascii')[1181:1230])
				# print(raw.decode('utf-8')[1181:1230])
				# print(raw.decode('ISO-8859-1')[1181:1230])
				# print(b'\xED\xB2\x80'.decode('utf-8'))
				bytes_string.decode('utf-8')
			except UnicodeDecodeError:
				return False
			else:
				for ch in bytes_string:
					if 0xD800 <= ord(ch) <= 0xDFFF:
						return False
				return True

		if is_ascii():
			return 'ascii'
		if is_utf8_strict():
			return 'utf-8'
		return ''

	def _mode_chardet(bytes_string):
		import chardet
		from chardet.universaldetector import UniversalDetector
		detect = chardet.detect(bytes_string)
		res_enc = detect['encoding']  # type: str
		try:
			res_enc = UniversalDetector.ISO_WIN_MAP[res_enc].lower()  # type: str
		except KeyError:
			enc_clean = res_enc.lower()
			try:
				res_enc = UniversalDetector.ISO_WIN_MAP[enc_clean].lower()  # type: str
			except KeyError:
				try:
					res_enc = UniversalDetector.ISO_WIN_MAP[enc_clean.replace('_', '-')].lower()  # type: str
				except KeyError:
					pass
		res_precision = detect['confidence']  # type: float
		return res_enc, res_precision

	def _mode_unicode_dammit(bytes_string):
		# u'<p>I just \u201clove\u201d Microsoft Word\u2019s smart quotes</p>'
		from bs4 import UnicodeDammit
		detected = UnicodeDammit(bytes_string)
		res_enc = detected.original_encoding  # type: str
		return res_enc, 0.5

	if mode == 0 or mode > 2:
		# try to detect using no external modules:
		detected = _mode_no_modules(raw)
		if detected:
			return detected, 1.0
		# we had no success. The next behavior depends on the mode:
		if mode == 0:
			# use the default system's encoding:
			import locale
			detected = locale.getpreferredencoding()  # type: str
			return detected, 0.0
		# continue detecting with the help of external modules:
		mode = mode - 2  # 3 -> 1; 4+ -> 2

	try:
		import chardet
	except ImportError as er_imp:
		_inst('chardet')

	if mode == 1:
		# actually, also mode 3 if no-modules approach didn't do the job
		return _mode_chardet(raw)

	# the 'UnicodeDammit+chardet' mode if we got here

	try:
		from bs4 import UnicodeDammit
	except ImportError as er_imp:
		_inst('beautifulsoup4')

	return _mode_unicode_dammit(raw)


def read_file_lines(
	file_path,  # type: Union[str, unicode]
	encoding=None,  # type: Optional[str]
	strip_newline_char=True
):
	"""
	High-level function reading a file at a given path (in a given encoding) as list of lines.

	If no encoding provided, read the file as raw strings.
	"""
	if not(
		isinstance(encoding, (str, unicode)) and encoding
	):
		# no encoding is provided
		with open(file_path, 'rt') as fl:
			if strip_newline_char:
				lines = [l.rstrip('\r\n') for l in fl]  # type: List[str]
			else:
				lines = list(fl)  # type: List[str]
	else:
		import io		# we do have an encoding
		with io.open(file_path, 'rt', encoding=encoding) as fl:
			if strip_newline_char:
				lines = [l.rstrip('\r\n') for l in fl]  # type: List[unicode]
			else:
				lines = list(fl)  # type: List[unicode]

	return lines
