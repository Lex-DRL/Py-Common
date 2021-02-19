__author__ = 'Lex Darlog (DRL)'
__all__ = (
	'file_dt_utc',
	'file_dt_local_tz',
)

from drl_common.py_2_3 import (
	path_h as _path_h,
)

import math as _math
import time as _time
from datetime import datetime as _dt
from os import path as _path

from pytz import utc as _utc  # $ pip install pytz
from tzlocal import get_localzone as _get_localzone  # $ pip install tzlocal


def file_dt_utc(
	file_path,  # type: _path_h
):
	"""
	Generate a datetime object from the given file's last modification date.
	The resulting time is in UTC timezone.
	"""
	file_date = _path.getmtime(file_path)
	microseconds = int(_math.modf(file_date)[0] * 1000000)
	file_date = _time.gmtime(file_date)
	return _dt(*(file_date[:6]), microsecond=microseconds, tzinfo=_utc)


def file_dt_local_tz(
	file_path,  # type: _path_h
):
	"""
	Generate a datetime object from the given file's last modification date.
	The resulting time is in local timezone.
	"""
	return file_dt_utc(file_path).replace(tzinfo=_utc).astimezone(_get_localzone())
