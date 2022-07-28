#!/usr/bin/env python
# encoding: utf-8
"""
"""

__author__ = 'Lex Darlog (DRL)'

# built-ins:
import errno
from fnmatch import fnmatch
import os
from pathlib import Path
from shutil import rmtree
import sys

# external packages:
import attrs as _a
import cattrs as _c

# internal packages:
from drl_os.config import json_config

# typing:
from typing import *


@_a.define
@json_config(attrs=True)
class Config:
	class JSON:
		user_path = '.drl/clear_temp'

	excluded: List[str] = [
		'houdini_temp',
		'hsperfdata_*'
	]


config = Config.json_load()


def clear_tmp_dir(dir_path: Union[None, AnyStr, Path] = None):
	if not dir_path or str(dir_path) in {'.', ''}:
		dir_path = os.getenv('TEMP')
	if not dir_path:
		dir_path = os.getenv('TMP')
	if not dir_path:
		raise OSError(errno.ENOENT, '<Empty path>')

	path: Path = dir_path if isinstance(dir_path, Path) else Path(dir_path)

	for child in path.iterdir():
		if any(fnmatch(child.name, x) for x in config.excluded):
			continue
		if child.is_dir():
			rmtree(child, ignore_errors=True)
			continue
		try:
			child.unlink()
		except OSError:
			pass


if __name__ == '__main__':
	args = sys.argv[1:]
	if not args:
		clear_tmp_dir()
	for a in args:
		clear_tmp_dir(a)
