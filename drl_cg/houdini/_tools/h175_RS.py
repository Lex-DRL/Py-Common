"""
Launch Houdini 17.5 with RedShift
"""

__author__ = 'Lex Darlog (DRL)'

from drl_cg import houdini
import sys


if __name__ == '__main__':
	reload(houdini)
	args = sys.argv[1:]
	houdini.launch('17.5.229', True, *args)
