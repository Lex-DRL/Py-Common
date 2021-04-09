"""Launch the given app with arguments and close the console window."""

__author__ = 'Lex Darlog (DRL)'

import sys

from drl_py23 import reload
from drl_os import process

reload(process)


if __name__ == '__main__':
	args = sys.argv[1:]
	process.start(sys.argv[1:])
