"""
Wrapper module providing python2/3 independent built-ins which were changed
in python 3. It's not a replacement but more of an extension to `__future__`.
"""

__author__ = 'Lex Darlog (DRL)'

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

try:
	raw_input = raw_input
except:
	raw_input = input
