__author__ = 'DRL'

from .__str_typing import *


py2 = False
py3 = False

try:
	# support type hints:
	import typing
	py3 = True
except ImportError:
	import __empty_module as typing
	py2 = True
	py3 = False

try:
	from itertools import izip, izip_longest
except ImportError:
	from itertools import zip_longest as izip_longest
	izip = zip
