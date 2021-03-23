"""Handy functions to work with OS environment."""

__author__ = 'Lex Darlog (DRL)'

# region the regular Type-Hints stuff

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass

from drl_py23 import (
	str_h as _str_h,
	str_t as _str_t,
	t_strict_unicode as _t_strict_unicode,
)

# endregion

import os as _os


def __to_str(val):
	if val is None:
		return ""
	if isinstance(val, _str_t):
		return val
	try:
		return str(val)
	except:
		return _t_strict_unicode(val)


def add_multi(
	append_in_front,  # type: bool
	*env_args,  # type: _t.Tuple[_str_h, _t.Any]
	**env_kwargs
):
	"""
	Set a bunch of environment variables at once.


	:param append_in_front:
		If `True`, new values will be appended at the beginning of a modified var.
		Otherwise, they're appended to the end.
	:param env_args:
		Extra env-vars as size-2 tuples with:
			* Name of the variable
			* value of the variable:
				* if `None` or empty string, removes (un-sets) the var
				*
					if current value of the var is not set yet or set to empty string,
					this value will be set as a new one
				* otherwise, the value is appended with delimiter

		If you want to force-reset var, you can provide two entries for the same
		var,  the first one as `None` and the second one with the ectual new value.
	:param env_kwargs:
		Similarly, some more env-vars.

		WARNING: since items order is undefined for dicts, this should not be used
		for re-setting already set env-vars. If they're present in system, the var
		value will be appended.

		The kwargs should only be used in very simple cases, where the var is
		definitely undefined or you intend to add the arg's value to it (e.g., PATH).
	"""
	if not (env_args or env_kwargs):
		return

	environ = _os.environ
	sep = _os.pathsep

	env_items = list(env_args)
	env_items.extend(
		(k, v) for k, v in env_kwargs.items()
	)

	for env_nm, new_val in env_items:
		if env_nm is None or not (env_nm and isinstance(env_nm, _str_t)):
			# force-throw an error of a wrong var name:
			prev_val = environ[env_nm]
		else:
			# get null if value isn't set yet:
			prev_val = environ.get(env_nm)

		# for any non-strings, force-convert it to string:
		new_val = __to_str(new_val)
		val_is_empty = (new_val == '')
		# we can't just bool() it ^ , there might be some custom class instance
		# that inherits from string, but redefines it's bool-casting

		if not prev_val:
			if not val_is_empty:
				environ[env_nm] = new_val
			continue

		if val_is_empty:
			# noinspection PyBroadException
			try:
				environ.pop(env_nm)
			except:
				environ[env_nm] = ''
			continue

		# general case: the var is already set and we have a non-empty value
		combined_val = sep.join(
			[new_val, prev_val] if append_in_front else [prev_val, new_val]
		)
		environ[env_nm] = combined_val

	return
