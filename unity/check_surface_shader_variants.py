__author__ = 'DRL'
from drl_common import filesystem as fs

class Check(object):
	__def_separator = '// -------- variant for:'
	__def_separator_lines = 2

	def __init__(self, file_path=None, separator=None, separator_lines=None):
		super(Check, self).__init__()
		if file_path:
			self.__set_filepath(file_path)
		else:
			self.__filepath = ''
		self.__lines = list()
		self.__sep = self.__def_separator
		self.__sep_lines = self.__def_separator_lines
		if not separator is None:
			self.separator = separator
		if not separator_lines is None:
			self.separator_lines = separator_lines

	def __set_filepath(self, filepath):
		if not isinstance(filepath, (str, unicode)):
			raise Exception("String expected as <filepath>. Got: " + repr(filepath))
		fs.error_if.path_not_readable(filepath)
		self.__filepath = filepath

	@property
	def file_path(self):
		if not self.__filepath:
			raise Exception("Trying to get <file_path> property while it's not set yet.")
		return self.__filepath
	@file_path.setter
	def file_path(self, value):
		self.__set_filepath(value)

	def read(self, strip_newline_character=True):
		file_path = self.file_path
		encoding = fs.detect_file_encoding(file_path, mode=1)[0]
		self.__lines = fs.read_file_lines(file_path, encoding, strip_newline_character)
		return self

	def lines(self):
		return self.__lines[:]

	@property
	def separator(self):
		return self.__sep
	@separator.setter
	def separator(self, value):
		if not isinstance(value, (str, unicode, unichr)):
			raise Exception('Wrong type. String expected. Got: ' + repr(value))
		self.__sep = value

	@property
	def separator_lines(self):
		return self.__sep_lines
	@separator_lines.setter
	def separator_lines(self, value):
		if not isinstance(value, int):
			raise Exception('Wrong type. Int expected. Got: ' + repr(value))
		self.__sep_lines = value

	def split_to_groups(self):
		prev = None
		lines = self.lines()
		sep = self.separator
		skip_delta = self.separator_lines

		groups = list()

		for i, ln in enumerate(lines):
			if i < prev:
				continue

			assert isinstance(ln, (str, unicode, unichr))
			if ln.startswith(sep):
				groups.append(lines[prev:i])
				prev = i + skip_delta

		if not prev + 1 > len(lines):
			groups.append(lines[prev:])

		return groups

	def different_groups(self):
		groups = self.split_to_groups()
		if len(groups) < 3:
			return []
		groups = groups[1:]
		gr1 = groups[0]
		res = list()
		for i, gr in enumerate(groups[1:]):
			if gr != gr1:
				res.append(i + 2)
		return res