"""
"""

__author__ = 'Lex Darlog (DRL)'

import sys
from os import path
from xml.etree import ElementTree

from drl_common import (
	drl_csv,
	filesystem as fs,
)
from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
)


cmd_args = sys.argv


def _check_type(value, correct_type, converted_type, error_message):
	if isinstance(value, converted_type):
		value = correct_type(value)
	if not isinstance(value, correct_type):
		raise TypeError(error_message + repr(value))
	return value


class DataItem(object):
	def __init__(self, asset_name='', percentage=0.0, size_raw=0, size_imported=0):
		super(DataItem, self).__init__()
		self.__set_name(asset_name)
		self.__set_percentage(percentage)
		self.__set_size_raw(size_raw)
		self.__set_size_imported(size_imported)

	def __set_name(self, value):
		if not isinstance(value, _str_t):
			raise TypeError("String value expected for <asset_name> property. Got: " + repr(value))
		self.__asset_name = value

	@property
	def asset_name(self):
		assert isinstance(self.__asset_name, _str_t)
		return self.__asset_name

	@asset_name.setter
	def asset_name(self, value):
		self.__set_name(value)

	def __set_percentage(self, value):
		self.__percentage = _check_type(
			value, float, int,
			"Float value expected for <percentage> property. Got: "
		)

	@property
	def percentage(self):
		assert isinstance(self.__percentage, float)
		return self.__percentage

	@percentage.setter
	def percentage(self, value):
		self.__set_percentage(value)

	def __set_size_raw(self, value):
		self.__size_raw = _check_type(
			value, int, float,
			"Integer value expected for <size_raw> property. Got: "
		)

	@property
	def size_raw(self):
		assert isinstance(self.__size_raw, int)
		return self.__size_raw

	@size_raw.setter
	def size_raw(self, value):
		self.__set_size_raw(value)

	def __set_size_imported(self, value):
		self.__size_imported = _check_type(
			value, int, float,
			"Integer value expected for <size_imported> property. Got: "
		)

	@property
	def size_imported(self):
		assert isinstance(self.__size_imported, int)
		return self.__size_imported

	@size_imported.setter
	def size_imported(self, value):
		self.__set_size_imported(value)

	def __repr__(self):
		return '<DataItem>: %s\t%s' % (self.size_imported, self.asset_name)


def get_data(f):
	# f = 'e:\\1-Projects\\2-Arena\\UnityProject\\UnityProject--2016Apr27-204708.xml'
	fs.error_check.file_readable(f)
	root = ElementTree.parse(f)
	used_assets = root.getroot().find('UsedAssets/All')
	res = []
	for a in used_assets:
		name = a.find('Name').text
		if isinstance(name, _str_t) and (
			name.endswith('.shader') or name.endswith('.cginc')
		):
			res.append(DataItem(
				asset_name=name,
				percentage=float(a.find('Percentage').text),
				size_raw=int(float(a.find('DerivedSize').text)),
				size_imported=int(float(a.find('ImportedSizeBytes').text))
			))
	res.sort(key=lambda x: x.asset_name)
	res.sort(key=lambda x: x.size_imported, reverse=True)
	return res


def size_to_beauty(size):
	size = _check_type(size, float, int, 'Int/Float value expected. Got: ')
	if size >= 1024:
		# kilo:
		size /= 1024
		if size >= 1024:
			# mega:
			size /= 1024
			if size >= 1024:
				# giga:
				return '%s GB' % round(size / 1024, 3)
			return '%s MB' % round(size, 3)
		return '%s KB' % round(size, 3)
	return '%s B' % int(size)


def data_to_csv_list(data):
	if not isinstance(data, (list, tuple)):
		raise TypeError('List expected. Got: ' + repr(data))
	if not data:
		return []

	res = [
		[
			'Asset',
			'Imported size', 'Imported size (bytes)',
			'Percentage',
			'Source asset size', 'Source asset size (bytes)'
		]
	]
	for a in data:
		if not isinstance(a, DataItem):
			raise TypeError('Wrong element type in data array. Expected <DataItem>, got: ' + repr(a))
		res.append([
			a.asset_name,
			size_to_beauty(a.size_imported), a.size_imported,
			a.percentage,
			size_to_beauty(a.size_raw), a.size_raw
		])
	return res


if cmd_args and len(cmd_args) > 1:
	files = cmd_args[1:]
	# cmd_args = ['e:\\1-Projects\\2-Arena\\UnityProject\\UnityProject--2016Apr27-204708.xml']
	for fl in files:
		# f = 'e:\\1-Projects\\2-Arena\\UnityProject\\UnityProject--2016Apr27-204708.xml'
		csv_data = data_to_csv_list(get_data(fl))
		out_csv = path.splitext(fl)[0] + '.csv'
		fs.clean_path_for_file(out_csv, overwrite_folders=1, remove_file=1)
		drl_csv.write_csv(csv_data, out_csv)
