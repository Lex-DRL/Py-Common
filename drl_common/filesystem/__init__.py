__author__ = 'DRL'

import os
import io
from os import path as _pth
import shutil as sh

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)
try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

import drl_common.errors as err
from drl_common import utils
from . import errors, error_check, file_time
from modules import pip_install as _inst
from drl_common import is_maya as _im
from drl_common.py_2_3.enum import EnumDefault as __EnumDefault

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


def __convert_path_slashes(
	path, wrong_slash='\\', right_slash='/', trailing_slash=None, leading_slash=0
):
	err.NotStringError(path, 'path').raise_if_needed()
	if not path:
		return ''

	assert isinstance(path, _str_t)
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


def to_unix_path(path, trailing_slash=None, leading_slash=False):
	"""
	Ensures given path has unix-style slashes. ("\" -> "/")

	:type path: str|unicode
	:param trailing_slash:
		Whether we need to ensure path has or lacks trailing slash:
			*
				`None`: (default) no check performed.
				Leave as is, just replace path slashes.
			* `False`: Force-remove trailing slash
			* `True`: Force-leave (single) trailing slash.
	:type trailing_slash: bool|None
	:param leading_slash:
		The same for leading slash.
		However, it's `False` (force-removed) by default.
	:type leading_slash: bool|None
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
		* NotExist - the path starts with a disk which doesn't exist.
		* UnknownObject - any of breadcrumbs is not a folder nor a file.
		* ParentFolderIsFile - a breadcrumb is a file, and overwrite is disabled.
	"""
	# path = r'e:\1-Projects\0-Common_Code\qqq\\'
	path = to_unix_path(path, trailing_slash=False)
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
		raise errors.NotExist(checked, "No such disk found in system")

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
		# path already exist:

		if os.path.isdir(item):
			return
		if not os.path.isfile(item):
			raise errors.UnknownObject(item)
		# we're facing a file (not a dir):

		if __is_overwrite_enabled(overwrite, item):
			os.remove(item)
			os.makedirs(item)
			return
		raise errors.ParentFolderIsFile(path, item, overwrite)

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
		raise errors.UnknownObject(path)

	if __is_overwrite_enabled(overwrite, path):
		os.remove(path)
		os.makedirs(path)
		return path

	raise errors.FileAlreadyExist(path, overwrite)


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
			*
				2 or more when called from Maya: display interactive dialog allowing a user to choose.
				When called outside of Maya, considered as <True>.
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
	)  # type: _str_hint
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
		raise errors.FileAlreadyExist(path, overwrite_folders, 'Folder already exist at the file path')

	raise errors.UnknownObject(path)

# ---------------------------------------------------------


class DetectEncodingMode(__EnumDefault):
	"""
	The modes supported by encoding detection for txt-file.

	No external dependencies:
		*
			**BUILT_IN**: Detect only `ascii` or `utf-8` (with 1.0 precision) if
			possible, use the default system's codepage (with 0.0 precision) otherwise.

	Depending on external modules,
	the above "dummy" check (BOM/UTF-8/ASCII) is **NOT** performed:
		* **CHARDET**: use `chardet` module only.
		* **CHARDET_DAMMIT**: use `chardet` **WITH** `beautifulsoup4.UnicodeDammit`.

	A combination of both previous approaches.
	First, try to detect the encoding the "dummy" way (BOM/UTF-8/ASCII).
	Then, if no success, use the modules specified above:
		* **FALLBACK_CHARDET**
		* **FALLBACK_CHARDET_DAMMIT**

	"""

	# default:
	BUILT_IN = 0  # type: DetectEncodingMode

	CHARDET = 1  # type: DetectEncodingMode
	CHARDET_DAMMIT = 2  # type: DetectEncodingMode

	FALLBACK_CHARDET = 3  # type: DetectEncodingMode
	FALLBACK_CHARDET_DAMMIT = 4  # type: DetectEncodingMode


_detEncMode = DetectEncodingMode


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
	file_path,  # type: _str_hint
	limit=64*1024,  # 64 Kb
	mode=None  # type: _t.Optional[DetectEncodingMode, int]
):
	"""

	:param file_path: the path of file to read.
	:param limit: max amount of bytes read from the file. If non-int or 0 and less, read it entirely .
	:param mode:
		One of the options from ``DetectEncodingMode`` enum.
		**FALLBACK_CHARDET_DAMMIT** if omitted.
	:return:
		* `str` detected encoding
		* `float` how sure the detector is:
			* in **BUILT_IN** mode, 1.5 on success (to differentiate from the actual detection), 0.0 if default encoding returned
			* in `chardet` mode, the actual 'sureness' of detector
			* in `UnicodeDammit` mode, always excactly 2.5
	"""
	# file_path = r'p:\0-Unity\builtin_shaders\CGIncludes\AutoLight.cginc'
	import codecs

	# first, try to detect BOM.
	# an extension of: https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
	file_path = error_check.file_readable(file_path)
	try:
		first_bytes = min(32, _pth.getsize(file_path))  # int for now
		with open(file_path, 'rb') as fl_first:
			first_bytes = fl_first.read(first_bytes)  # str now
	except IOError:
		raise errors.NotReadable(file_path)
	for bom, enc in (
		(codecs.BOM_UTF32_BE, 'utf-32-be'),
		(codecs.BOM_UTF32_LE, 'utf-32-le'),
		(codecs.BOM_UTF8, 'utf-8-sig'),
		(codecs.BOM_UTF16_BE, 'utf-16-be'),
		(codecs.BOM_UTF16_LE, 'utf-16-le'),
	):
		if first_bytes.startswith(bom):
			return enc, 1.5
	del first_bytes

	if isinstance(mode, float):
		mode = int(mode)
	mode = _detEncMode.get(
		mode, default=_detEncMode.FALLBACK_CHARDET_DAMMIT
	)

	if not (isinstance(limit, int) and limit > 0):
		limit = None

	raw = ''
	try:
		with open(file_path, 'rb') as fl:
			raw = fl.read() if limit is None else fl.read(limit)
	except IOError:
			raise errors.NotReadable(file_path)

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

		def detect_utf8_strict():
			enc_utf = 'utf-8'
			try:
				# print(raw.decode('koi8-r')[1181:1230])
				# print(raw.decode('cp1252')[1181:1230])
				# print(raw.decode('ascii')[1181:1230])
				# print(raw.decode('utf-8')[1181:1230])
				# print(raw.decode('ISO-8859-1')[1181:1230])
				# print(b'\xED\xB2\x80'.decode('utf-8'))
				bytes_string.decode(enc_utf)
			except UnicodeDecodeError:
				enc_utf = 'utf-8-sig'
				try:
					bytes_string.decode(enc_utf)
				except UnicodeDecodeError:
					return None
			else:
				for ch in bytes_string:
					if 0xD800 <= ord(ch) <= 0xDFFF:
						return None
				return enc_utf

		if is_ascii():
			return 'ascii'
		detected_utf = detect_utf8_strict()
		if detected_utf:
			return detected_utf
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
		# noinspection PyProtectedMember
		from bs4 import UnicodeDammit
		detected_dammit = UnicodeDammit(bytes_string)
		res_enc = detected_dammit.original_encoding  # type: str
		return res_enc, 2.5

	if mode in {
		_detEncMode.BUILT_IN,
		_detEncMode.FALLBACK_CHARDET,
		_detEncMode.FALLBACK_CHARDET_DAMMIT
	}:
		# try to detect using no external modules:
		detected = _mode_no_modules(raw)
		if detected:
			return detected, 1.5
		# we had no success. The next behavior depends on the mode:
		if mode is _detEncMode.BUILT_IN:
			# use the default system's encoding:
			import locale
			detected = locale.getpreferredencoding()  # type: str
			return detected, 0.0
		# continue detecting with the help of external modules:
		mode = {
			_detEncMode.FALLBACK_CHARDET:        _detEncMode.CHARDET,
			_detEncMode.FALLBACK_CHARDET_DAMMIT: _detEncMode.CHARDET_DAMMIT,
		}[mode]

	try:
		import chardet
	except ImportError:
		try:
			_inst('chardet')
		except ImportError:
			_inst('pip chardet')

	if mode is _detEncMode.CHARDET:
		# actually, also FALLBACK_CHARDET if no-modules approach didn't do the job
		return _mode_chardet(raw)

	# the 'UnicodeDammit+chardet' mode if we got here

	try:
		# noinspection PyProtectedMember
		from bs4 import UnicodeDammit
	except ImportError:
		try:
			_inst('beautifulsoup4')
		except ImportError:
			_inst('pip beautifulsoup4')

	return _mode_unicode_dammit(raw)


def read_file_lines(
	file_path, encoding=None, strip_newline_char=True,
	line_process_f=None  # type: _t.Optional[_t.Callable[[_str_hint], _str_hint]]
):
	"""
	High-level function reading a file at as list of lines.
	It's benefit over default `open()` is that it supports a few common features
	which are enabled as simply as just passing an argument.

	:param file_path: the file path.
	:type file_path: str|unicode
	:param encoding:
		*
			`None`: read the file with the default `open()` command,
			with no decoding performed.
		*
			`str`: the file is decoded to the list of unicode strings,
			with the given encoding and a more advanced `io.open()` command.
	:type encoding: None|str
	:param strip_newline_char:
		When enabled (default), the trailing newline-char is removed from each line.
	:type strip_newline_char: bool
	:param line_process_f:
		An optional function processing a single line as file is being read.
		This lets you get a list of lines that are already processed,
		which is much more memory-effecient and performant then reading a file first
		and then processing the entire list as a whole new step.

		When provided and newline-char stripping is also enabled, the **stripping is
		performed first** (your function already gets a string with no trailing newline-char).
	"""
	error_check.file_readable(file_path)

	def _rstrip_with_processing(
		line_str  # type: _str_hint
	):
		return line_process_f(line_str.rstrip('\r\n'))

	def _rstrip_only(
		line_str  # type: _str_hint
	):
		return line_str.rstrip('\r\n')

	is_f_given = callable(line_process_f)
	if strip_newline_char:
		f = _rstrip_with_processing if is_f_given else _rstrip_only
	else:
		f = line_process_f if is_f_given else None

	if isinstance(encoding, (str, unicode)) and encoding:
		# we do have an encoding
		try:
			with io.open(file_path, 'rt', encoding=encoding) as fl:
				if f is None:
					lines = list(fl)  # type: _t.List[unicode]
				else:
					lines = [f(l) for l in fl]  # type: _t.List[unicode]
		except IOError:
			raise errors.NotReadable(file_path)
	else:
		# no encoding is provided
		try:
			with open(file_path, 'rt') as fl:
				if f is None:
					lines = list(fl)  # type: _t.List[str]
				else:
					lines = [f(l) for l in fl]  # type: _t.List[str]
		except IOError:
			raise errors.NotReadable(file_path)

	return lines


def read_file_lines_best_enc(
	file_path,  # type: _str_hint
	strip_newline_char=True,
	line_process_f=None,  # type: _t.Optional[_t.Callable[[_str_hint], _str_hint]]
	detect_limit=64*1024,  # 64 Kb
	detect_mode=None,
	sure_thresh=0.5
):
	"""
	A wrapper, combining `detect_file_encoding()` and `read_file_lines()` and
	a few different read attempts into a single function, which should try read
	a file with an unknown encoding the best way possible.

	First, it detects a file encoding. Then it reads it:
		*
			If detected 'sureness' is enough (higher or equal to `sure_thresh`),
			read the file using detected enc.
		* If not, try to read as ascii first.
		*
			If still no success, with no encoding at all (using the basic `open()`,
			not `io.open()`).

	For any argument other than `sure_thresh`, consult either
	``detect_file_encoding()`` or ``read_file_lines()``.

	:return:
		* `List of strings/unicodes` - the read file lines.
		* `string` encoding on success, `None` if the basic `open()` was used.
		* `float` how sure the detector is about it's encoding.
	"""
	encoding, enc_sure = detect_file_encoding(
		file_path, limit=detect_limit, mode=detect_mode
	)
	not_enough_sure = bool(enc_sure < sure_thresh)
	if not_enough_sure or not encoding:
		try:
			encoding = 'ascii'
			lines = read_file_lines(
				file_path, encoding, strip_newline_char, line_process_f
			)
			if not_enough_sure:
				enc_sure = 1.0
		except UnicodeDecodeError:
			encoding = None
			lines = read_file_lines(
				file_path, encoding, strip_newline_char, line_process_f
			)
	else:
		lines = read_file_lines(
			file_path, encoding, strip_newline_char, line_process_f
		)

	return lines, encoding, enc_sure


def write_file_lines(
	file_path,  # type: _str_hint
	lines,  # type: _t.Union[_str_hint, _t.Iterable[_str_hint]]
	encoding=None,  # type: _t.Optional[str]
	newline='\n',  # type: _t.Optional[str]
	newline_included=False
):
	file_path = error_check.file_writeable(file_path)

	def open_io():
		return io.open(file_path, 'wt', encoding=encoding, newline=newline)

	def open_default():
		return open(file_path, 'wt')

	open_f = open_default if (encoding is None and newline is None) else open_io
	# lines = '\n'.join(lines)

	try:
		with open_f() as fl:
			if isinstance(lines, _str_t):
				fl.write(lines)
			else:
				if (newline is None or newline != '') and not newline_included:
					lines = (l + '\n' for l in lines)
				fl.writelines(lines)
	except IOError:
		raise errors.NotWriteable(file_path)


def dir_tree_gen(
	root,  # type: _str_hint
	topdown=True,
	onerror=None,  # type: _t.Optional[_t.Callable[[OSError], _t.Any]]
	followlinks=False,
	trailing_slash=False
):
	"""
	A wrapper on top of `os.walk()`, providing a flat sequence of the whole directory tree.
	Path separators are always unix-style slashes.

	:param trailing_slash: If `True`, all the directories will have a trailing slash.
	"""
	if not (root and isinstance(root, _str_t)):
		return
	# root = r'f:\1-Archive\Photos\_Phone-Camera\chair'
	# root = 'f'
	root = root[0] + root[1:].replace('\\', '/').rstrip('/')

	def _cleanup_cur_root_trailed(
		rt  # type: _str_hint
	):
		rt = rt.replace('\\', '/')
		trailed = rt[0] + rt[1:].rstrip('/') + '/'
		if trailed == '//':
			trailed = trailed[0]  # to preserve unicode
		return trailed, trailed

	def _cleanup_cur_root_no_trail(
		rt  # type: _str_hint
	):
		rt = rt.replace('\\', '/')
		no_trail = rt[0] + rt[1:].rstrip('/')
		trailed = no_trail + '/'
		if trailed == '//':
			trailed = trailed[0]  # to preserve unicode
		return no_trail, trailed

	_cleanup_cur_root = _cleanup_cur_root_trailed if trailing_slash else _cleanup_cur_root_no_trail

	for cur_root, dirs, files in os.walk(root, topdown=topdown, onerror=onerror, followlinks=followlinks):
		cur_root, cur_trailed = _cleanup_cur_root(cur_root)
		yield cur_root
		for fl in files:
			yield cur_trailed + fl
