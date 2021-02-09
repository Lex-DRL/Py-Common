__author__ = 'Lex Darlog (DRL)'

import os
import sys
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_h as _str_h,
)
from drl_cg.nuke import launch_nk_process as _launch_nk
from drl_cg.nuke.processor import errors as _err

nk_file = r'exr_to_png_RGB.nk'

cmd_args = sys.argv[1:]

# cmd_args = [
# 	r'E:\5-Internet\Dropbox\0-Settings\Python\for_nuke\post-bake_turtle_unity.nk',
# 	r'e:\1-Projects\5-ShaderFX\sources\Trash\Trash.exr',
# 	r'e:\1-Projects\5-ShaderFX\sources\Trash\Trash.png',
# 	'qqq',
# 	'zzz'
# ]

if not cmd_args:
	raise _err.NoPathError()

files_to_process = []


def append_to_list(p):
	if isinstance(p, _str_t) and os.path.exists(p):
		if os.path.isfile(p) and os.path.splitext(p)[-1].lower() == '.exr':
			files_to_process.append(p)
			return
		if os.path.isdir(p):
			append_to_list([os.path.join(p, f) for f in os.listdir(p)])
			return

	if isinstance(p, (list, tuple, set)):
		for n_p in p:
			append_to_list(n_p)
		return

append_to_list(cmd_args)

for f in files_to_process:
	out = os.path.splitext(f)[0] + '.png'
	print (f + '\n' + out + '\n')
	_launch_nk.process(
		f, out, nk_script=nk_file, auto_to_exr=False, post_wait=0.0
	)

print u'Done.\nPress <Enter> to finish...'
raw_input()
