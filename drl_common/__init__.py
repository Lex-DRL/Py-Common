__author__ = 'DRL'


def module_string(name, start=-3, end=-1):
	assert isinstance(name, (str, unicode))
	return '[%s]' % '.'.join(
		name.split('.')[start:end]
	)