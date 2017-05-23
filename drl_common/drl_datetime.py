__author__ = 'DRL'

import datetime as dt


def scale_timedelta(timedelta, scale=1.0):
	if not isinstance(timedelta, dt.timedelta):
		raise TypeError("datetime.timedelta expected. Got: " % timedelta)
	if not isinstance(scale, (float, int)):
		raise TypeError("Float or int scale expected expected. Got: " % scale)

	if scale < 0.0:
		scale = abs(scale)
		timedelta = -timedelta

	if scale == 1.0:
		return timedelta

	if scale == int(scale):
		return timedelta * int(scale)

	total_secs = timedelta.total_seconds() * scale
	int_secs = int(total_secs)
	int_mksec = int(float(total_secs - int_secs) * 1000000.0)
	return dt.timedelta(seconds=int_secs, microseconds=int_mksec)