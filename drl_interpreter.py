"""
A module detecting under which python interpreter the script is running.
"""

__author__ = 'Lex Darlog (DRL)'

# noinspection PyBroadException,PyPep8
try:
	# noinspection PyUnresolvedReferences
	_str_t = (str, unicode)
except:
	_str_t = (str, bytes)


def __test_if_maya():
	try:
		from maya import cmds
	except ImportError:
		return False

	cmds_path = cmds.__file__.replace('\\', '/')
	assert isinstance(cmds_path, _str_t)
	path_split = cmds_path.split('/')
	if (
		len(path_split) > 4 and
		'completion' in path_split[-6:] and
		any((x in path_split[-5:]) for x in['py', 'pi'])
	):
		# we have actually found a devkit's completion, not really in maya:
		return False

	return True


def __test_if_hou():
	try:
		from hou import node
	except ImportError:
		return False

	if not callable(node):
		return False

	return True


is_maya = __test_if_maya()
is_hou = __test_if_hou()
