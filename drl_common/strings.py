__author__ = 'DRL'

str_types = (str, unicode, unichr)


def error_if_not_str(var, var_name="variable"):
	if not isinstance(var_name, str_types) or not var_name:
		var_name = "variable"
	if not isinstance(var, str_types):
		raise Exception(
			'The {0} needs to be a string or unicode. Got: {1}'.format(var_name, str(var))
		)