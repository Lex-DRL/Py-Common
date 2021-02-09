__author__ = 'DRL'

import csv

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_h as _str_h,
	t_strict_unicode as _unicode,
)

def __get_dialect(file_handle, dialect=None):
	if dialect is None:
		dialect = csv.Sniffer().sniff(file_handle.read(1024))
		file_handle.seek(0)
	return dialect


def read_csv(csv_file='', dialect=None, utf8=False, **kwargs):
	with open(csv_file, 'rb') as fl:
		if utf8:
			fl = utf_8_encoder(fl)
		dialect = __get_dialect(fl, dialect)
		reader = csv.reader(fl, dialect, **kwargs)
		if utf8:
			for row in reader:
				yield [_unicode(cell, 'utf-8') for cell in row]
		else:
			for row in reader:
				yield row


def write_csv(data, csv_file='', dialect='excel-tab', **kwargs):
	with open(csv_file, 'wb') as fl:
		writer = csv.writer(fl, dialect, **kwargs)
		writer.writerows(data)


def read_csv_data(csv_file='', dialect=None, utf8=False, **kwargs):
	res = []
	for row in read_csv(csv_file, dialect=dialect, utf8=utf8, **kwargs):
		res.append(row)
	return res


def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')