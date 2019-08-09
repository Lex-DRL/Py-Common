__author__ = 'DRL'

# only for backward compatibility in legacy code:
from .cols import Container, DefaultList, DefaultTuple


def module_string(name, start=-3, end=-1):
	assert isinstance(name, (str, unicode))
	return '[%s]' % '.'.join(
		name.split('.')[start:end]
	)
