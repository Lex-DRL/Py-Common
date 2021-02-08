__author__ = 'DRL'

from .__str_typing import *


py2 = False
py3 = False

try:
	# support type hints:
	import typing
	py3 = True
except ImportError:
	import __typing_fallback as typing
	py2 = True
	py3 = False

try:
	from itertools import izip, izip_longest
except ImportError:
	from itertools import zip_longest as izip_longest
	izip = zip

try:
	xrange = xrange
except NameError:
	xrange = range

try:
	reload = reload
except:
	from importlib import reload


if py2:
	from .__monkey_patchers_py2 import _all as __patchers
if py3:
	from .__monkey_patchers_py3 import _all as __patchers
if py2 or py3:
	for patcher in __patchers:
		patcher()
	del __patchers
