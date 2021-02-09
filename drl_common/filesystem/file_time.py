__author__ = 'Lex Darlog (DRL)'

import math as _m
import time as _t
from datetime import datetime as _dt
from os import path as _path

from drl_common import timezones as _tz


def file_dt_utc(file_path):
	"""
	Generate a datetime object from the given file's last modification date.
	The resulting time is in UTC timezone.

	:param file_path: <str>
	:return: <datetime> instance
	"""
	utc_error = _tz.utc_error
	if not(utc_error is None):
		raise utc_error

	file_date = _path.getmtime(file_path)
	microseconds = int(_m.modf(file_date)[0] * 1000000)
	file_date = _t.gmtime(file_date)
	return _dt(*(file_date[:6]), microsecond=microseconds, tzinfo=_tz.utc)


def file_dt_local_tz(file_path):
	"""
	Generate a datetime object from the given file's last modification date.
	The resulting time is in local timezone.

	:param file_path: <str>
	:return: <datetime> instance
	"""
	utc_error = _tz.utc_error
	if not(utc_error is None):
		raise utc_error

	local_error = _tz.local_error
	if not(local_error is None):
		raise local_error

	return file_dt_utc(file_path).replace(tzinfo=_tz.utc).astimezone(_tz.get_local())
