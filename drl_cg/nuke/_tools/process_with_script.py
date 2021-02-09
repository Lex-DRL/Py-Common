__author__ = 'Lex Darlog (DRL)'

import os
import sys
import time

cmd_args = sys.argv[:]
print(cmd_args)
# cmd_args = [
# 	r'E:\5-Internet\Dropbox\0-Settings\Python\for_nuke\process_with_script.py',
# 	r'E:\5-Internet\Dropbox\0-Settings\Python\for_nuke\post-bake_turtle_unity.nk',
# 	r'e:\1-Projects\5-ShaderFX\sources\Trash\Trash.exr',
# 	r'e:\1-Projects\5-ShaderFX\sources\Trash\Trash.png',
# 	'qqq',
# 	'zzz'
# ]


sleep_time = 3.0

nk_script = cmd_args[1].replace('\\', '/')
src_path = cmd_args[2].replace('\\', '/')
# src_path = r'e:\1-Projects\5-ShaderFX/sources\Trash\Trash.exr'


def get_out_path():
	if len(cmd_args) > 3 and cmd_args[3]:
		out_path = cmd_args[3].replace('\\', '/')
		# out_path = r'e:\1-Projects\5-ShaderFX\sources\Trash\Trash'.replace('\\', '/')
		path, ext = os.path.splitext(out_path)
		if ext.lower() in ['.png', '.exr']:
			return out_path
		return path + '.png'
	return os.path.splitext(src_path)[0] + '.png'


out_path = get_out_path()

read_node_name = cmd_args[4] if len(cmd_args) > 4 else 'Read_in'

write_node_name = 'Write_out'
if os.path.splitext(out_path)[1].lower() == '.exr':
	write_node_name = 'Write_out_EXR'
if len(cmd_args) > 5:
	write_node_name = cmd_args[5]

import nuke as nk
from drl_common import filesystem as fs

print('Waiting for %s seconds...' % sleep_time)
time.sleep(sleep_time)

print("Opening nuke script: " + nk_script)
nk.scriptOpen(nk_script)
r = nk.toNode(read_node_name)
r['file'].setValue(src_path)
print("Set read-file to: " + src_path)

w = nk.toNode(write_node_name)
w['file'].setValue(out_path)
print("Set write-file output to: " + out_path)
fs.clean_path_for_file(out_path, overwrite_folders=1, remove_file=1)
nk.execute(w, 1,1,1, continueOnError=False)
print("File rendered.")

print('Waiting for %s seconds...' % sleep_time)
time.sleep(sleep_time)
