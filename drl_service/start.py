"""A generic script launching an app with arguments"""

__author__ = 'Lex Darlog (DRL)'

if __name__ == '__main__':
	import sys, time
	from drl_common.py_2_3 import reload
	from drl_os import process
	reload(process)
	
	args = sys.argv[1:]
	print (args)
	process.start(args)
	time.sleep(3)
