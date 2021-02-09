__author__ = 'DRL'

from drl_common.py_2_3 import (
	str_t as _str_t,
	str_h as _str_h,
)

# only for backward compatibility in legacy code:
from .cols import Container, DefaultList, DefaultTuple


def module_string(name, start=-3, end=-1):
	assert isinstance(name, _str_t)
	return '[%s]' % '.'.join(
		name.split('.')[start:end]
	)
