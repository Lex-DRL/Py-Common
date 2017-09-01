__author__ = 'DRL'

import inspect as _inspect


class NotTypeError(TypeError):
	"""
	This exception is thrown when a type is expected,
	but instead the actual value is provided.
	"""
	def __init__(self, val=None, object_name=''):
		msg = 'Type is expected'

		if object_name:
			msg += " for <{0}>.".format(object_name)
		else:
			msg += "."

		if val is None:
			msg += ' Got the actual value instead.'
		else:
			msg += ' Got: {0}'.format(repr(val))

		super(NotTypeError, self).__init__(msg)
		self.object_name = object_name
		self.value = val

	def raise_if_not_type(self):
		"""
		Raises self, if the provided value is not a type.

		:return: The value, if it's OK.
		"""
		val = self.value
		if not isinstance(val, type):
			raise self
		return val

	def raise_if_wrong_arg_for_isinstance(self):
		"""
		Raises self, if the provided value can't be passed to the isinstance() function
		as the 2nd argument (allowed types).

		:return: The value, if it's OK.
		"""
		val = self.value
		if isinstance(val, tuple):
			if all([isinstance(t, type) for t in val]):
				return val
			raise self
		return self.raise_if_not_type()


class WrongTypeError(TypeError):
	"""
	The given value doesn't match expected type.
	This error is inherited from TypeError, but it's more descriptive and easy-to-use.

	:param val: source value
	:param types: permitted types this value may take
	:param var_name: optional string containing the name of the checked variable (for easier debug).
	:param types_name: optional string containing the beautiful name for permitted types.
	"""
	def __init__(self, val, types=None, var_name=None, types_name=None):
		msg = (
			'Wrong type provided for <%s>.' % var_name
			if isinstance(var_name, (str, unicode)) and var_name else
			'Wrong type provided.'
		)
		types_given = True
		if not (isinstance(types_name, (str, unicode)) and types_name):
			if types is None:
				types_given = False
			else:
				types_name = repr(types)

		if types_given:
			msg += ' Expected: {0}, got: {1}.'.format(types_name, repr(val))

		super(WrongTypeError, self).__init__(msg)
		self.value = val
		self.var_name = var_name
		self.types = types
		self.types_name = types_name
		self.is_types_name_provided = types_given

	def raise_if_needed(self):
		"""
		Raise self if type is wrong.

		:return: given value (asserted to be of given type)
		"""
		val = self.value
		types = self.types
		if not isinstance(val, types):
			raise self
		assert isinstance(val, types)
		return val

	def raise_by_condition(self, condition_f=None):
		"""
		Raise self if the provided value matches the given condition.

		:param condition_f:
			*
				<function>, which can receive from 0 to 2 arguments:

				func([value [, types]])
			*
				None / not callable: always raise.

				I.e., you can call self.raise_by_condition() *(with no arguments)*
				to force raising the error

			:raise self: when condition_f() is true
		:return: given value if condition returns False
		"""
		if (condition_f is None) or not callable(condition_f):
			raise self

		try:
			num_args = len(_inspect.getargspec(condition_f).args)
		except:
			num_args = 1

		val = self.value
		if num_args > 1:
			do_raise = condition_f(val, self.types)
		elif num_args == 1:
			do_raise = condition_f(val)
		else:
			do_raise = condition_f()

		if do_raise:
			raise self
		return val


def _raise_by_condition_for_value(self, val, condition_f=None):
		"""
		Raise self if the provided value matches the given condition.

		:param self: the instance of the **Error** class.
		:param val: tested value.
		:param condition_f:
			*
				<function>, which can receive 0 or 1 argument:

				func([value])
			*
				None / not callable: always raise.

				I.e., you can call _raise_by_condition_for_value() *(with no arguments)*
				to force raising the error

			:raise self: when condition_f() is true
		:return: given value if condition returns False
		"""
		if (condition_f is None) or not callable(condition_f):
			raise self

		try:
			num_args = len(_inspect.getargspec(condition_f).args)
		except:
			num_args = 0

		if num_args == 1:
			do_raise = condition_f(val)
		else:
			do_raise = condition_f()

		if do_raise:
			raise self
		return val



class EmptyStringError(ValueError):
	def __init__(self, var_name=None):
		msg = (
			'Empty string provided for <%s>.' % var_name
			if isinstance(var_name, (str, unicode)) and var_name else
			'Empty string provided.'
		)
		super(EmptyStringError, self).__init__(msg)
		self.var_name = var_name

	def raise_if_empty(self, val):
		"""
		Raise self if bool(val) is False.

		:param val: <str> tested value.
		:return: given value (asserted it's string).
		"""
		if not val:
			raise self
		assert (val != '')
		return val

	def raise_by_condition(self, val, condition_f=None):
		"""
		Raise self if the provided value matches the given condition.

		:param val: tested value.
		:param condition_f:
			*
				<function>, which can receive 0 or 1 argument:

				func([value])
			*
				None / not callable: always raise.

				I.e., you can call self.raise_by_condition() *(with no arguments)*
				to force raising the error

			:raise self: when condition_f() is true
		:return: given value if condition returns False
		"""
		return _raise_by_condition_for_value(self, val, condition_f)


class NoValueError(ValueError):
	def __init__(self, var_name=None):
		msg = (
			'No value provided for <%s>.' % var_name
			if isinstance(var_name, (str, unicode)) and var_name else
			'No value provided.'
		)
		super(NoValueError, self).__init__(msg)
		self.var_name = var_name

	def raise_if_false(self, val):
		"""
		Raise self if bool(val) is False.

		:param val: tested value.
		:return: given value (asserted it has non-False value).
		"""
		if not val:
			raise self
		assert bool(val)
		return val

	def raise_if_none(self, val):
		"""
		Raise self if given value is None.

		:param val: tested value.
		:return: given value (asserted it's not None).
		"""
		if val is None:
			raise self
		assert not(val is None)
		return val

	def raise_by_condition(self, val, condition_f=None):
		"""
		Raise self if the provided value matches the given condition.

		:param val: tested value.
		:param condition_f:
			*
				<function>, which can receive 0 or 1 argument:

				func([value])
			*
				None / not callable: always raise.

				I.e., you can call self.raise_by_condition() *(with no arguments)*
				to force raising the error

			:raise self: when condition_f() is true
		:return: given value if condition returns False
		"""
		return _raise_by_condition_for_value(self, val, condition_f)


class WrongValueError(ValueError):
	"""
	The given value doesn't match what's expected.
	This error is inherited from ValueError, but it's more descriptive and easy-to-use.

	:param val: source value
	:param var_name: optional string containing the name of the checked variable (for easier debug).
	:param expected_value: optionally specify the expected value. It could be either a value itself or it's string description.
	"""
	def __init__(self, val, var_name=None, expected_value=None):
		msg = (
			'Wrong value provided for <%s>.' % var_name
			if isinstance(var_name, (str, unicode)) and var_name else
			'Wrong value provided.'
		)
		if expected_value is None:
			msg += ' Got: {0}.'.format(val.__repr__())
		else:
			msg += ' Expected: {0}. Got: {1}.'.format(expected_value, val.__repr__())

		super(WrongValueError, self).__init__(msg)
		self.value = val
		self.var_name = var_name
		self.expected_value = expected_value

	def raise_by_condition(self, condition_f=None):
		"""
		Raise self if the provided value matches the given condition.

		:param condition_f:
			*
				<function>, which can receive 0 or 1 argument:

				func([value])
			*
				None / not callable: always raise.

				I.e., you can call self.raise_by_condition() *(with no arguments)*
				to force raising the error

			:raise self: when condition_f() is true
		:return: given value if condition returns False
		"""
		return _raise_by_condition_for_value(self, self.value, condition_f)


class NotStringError(WrongTypeError):
	"""
	The given value isn't a string (not str nor unicode).

	:param val: source value
	:param var_name: optional string containing the name of the checked variable (for easier debug).
	"""
	def __init__(self, val, var_name=None):
		super(NotStringError, self).__init__(val, (str, unicode), var_name, 'string')

	def raise_if_needed_or_empty(self):
		"""
		Raise self if given value is either not a string or is empty.

		:return: given value (asserted it's string and non-empty)
		"""
		val = self.raise_if_needed()
		return EmptyStringError(self.var_name).raise_if_empty(val)