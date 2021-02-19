__author__ = 'Lex Darlog (DRL)'

from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
)

__is_maya = True
try:
	from maya import cmds
except ImportError:
	__is_maya = False

if __is_maya:
	_path = cmds.__file__.replace('\\', '/')
	assert isinstance(_path, _str_t)
	_split = _path.split('/')
	if (
		len(_split) > 4 and
		'py' in _split[-5:] and
		'completion' in _split[-6:]
	):
		# we have actually found a devkit's completion, not really in maya:
		__is_maya = False
	del cmds
	del _path
	del _split


def is_maya():
	"""
	Whether python interpreter is Maya.
	"""
	return __is_maya
