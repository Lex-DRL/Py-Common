# encoding: utf-8
"""
Defines `static_class` decorator.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	import attrs as _a
	_have_attrs_package = True
except ImportError:
	_have_attrs_package = False


def _call_repr(cls_name, *args, **kwargs):
	args_repr = [repr(x) for x in args]
	args_repr.extend('{0}={1}'.format(k, repr(v)) for k, v in kwargs.items())
	return '{cls_nm}({args})'.format(cls_nm=cls_name, args=', '.join(args_repr))


# noinspection PyDecorator
@classmethod
def __new__(cls, name, *args, **kwargs):
	raise TypeError(
		'Attempt to create an instance of STATIC {cls_tp_repr}: {call_repr}'.format(
			cls_tp_repr=name,
			call_repr=_call_repr(cls.__name__, *args, **kwargs),
		)
	)


def static_class(cls=None, *_, to_attrs=True, ):
	"""
	Decorator defining a static class. I.e., the one that forbids `__init__` call to create an instance. When an `attrs` package is installed and `to_attrs` is `True` (default), also defines
	the class as an attrs-style one, as: `attrs.define(init=False, frozen=True)`.

	If you want to explicitly specify other attrs parameters or make it a regular class altogether, you can
	disable this behavior with `to_attrs=False`.

	If used with manual explicit attrs decorator, `static_class` should be applied AFTER it (or any other decorator
	which might define `__init__()` method). I.e., `static_class` must be above `attrs.define`.
	"""

	def _wrap(cls):
		if to_attrs and _have_attrs_package:
			cls = _a.define(init=False, frozen=True)(cls)

		cls.__new__ = __new__
		return cls

	if cls is None:
		return _wrap
	return _wrap(cls)
