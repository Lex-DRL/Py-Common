__author__ = 'DRL'

__is_maya = True
try:
	from maya import cmds
except ImportError:
	__is_maya = False

if __is_maya:
	_path = cmds.__file__.replace('\\', '/')
	assert isinstance(_path, (str, unicode))
	_split = _path.split('/')
	if all((
		len(_split) > 4,
		_split[-4] == 'py' or _split[-5] == 'py',
		_split[-5] == 'completion' or _split[-6] == 'completion'
	)):
		__is_maya = False
	del cmds
	del _path
	del _split


def is_maya():
	"""
	Whether python interpreter is Maya.

	:return: <bool>
	"""
	return __is_maya
