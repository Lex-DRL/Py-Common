"""
Launch Houdini 16.5 with RedShift
"""

__author__ = 'Lex Darlog (DRL)'

from drl_cg import houdini
import sys


if __name__ == '__main__':
	reload(houdini)
	args = sys.argv[1:]
	houdini.launch('16.5.634', True, *args)
