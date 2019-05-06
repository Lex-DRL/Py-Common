__author__ = 'DRL'

from .utils import Container, DefaultList, DefaultTuple


def module_string(name, start=-3, end=-1):
	assert isinstance(name, (str, unicode))
	return '[%s]' % '.'.join(
		name.split('.')[start:end]
	)
