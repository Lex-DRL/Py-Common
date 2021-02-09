__author__ = 'Lex Darlog (DRL)'

# UTC from pytz
try:
	from pytz import utc  # $ pip install pytz
	utc_error = None
except ImportError as err:
	utc = None
	utc_error = err


# get_local from tzlocal
try:
	from tzlocal import get_localzone as get_local  # $ pip install tzlocal
	# since it could update during runtime,
	# it's up to higher-level module to decide whether to cache it or just call every time
	local_error = None
except ImportError as err:
	get_local = None
	local_error = err
