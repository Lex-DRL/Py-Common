__author__ = 'DRL'

import pytz as _pytz  # $ pip install pytz
import tzlocal as _tzlocal  # $ pip install tzlocal

UTC = _pytz.utc

# since it could update during runtime,
# it's up to higher-level module to decide whether to cache it or just call every time
get_local = _tzlocal.get_localzone