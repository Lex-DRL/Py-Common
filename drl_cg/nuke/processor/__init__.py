"""
"""

__author__ = 'Lex Darlog (DRL)'

from drl_py23 import (
	str_t as _str_t,
	str_h as _str_h,
)

from drl_common import (
	errors as _err_comm,
	filesystem as _fs,
)
from drl_os.files import error_check as _fl_error_check

from . import errors


class NukeProcessor(object):
	def __init__(
		self,
		src_tex, out_tex, explicit_to_exr=True
	):
		super(NukeProcessor, self).__init__()

		self._src_tex = tuple()
		self._out_tex = tuple()
		self._explicit_to_exr = bool(explicit_to_exr)

		self.__set_src_tex(src_tex)
		self.__set_out_tex(out_tex)

	@property
	def explicit_to_exr(self):
		"""
		When output texture isn't specified explicitly, this property defines
		whether extension of the resulting file will be EXR or PNG.

		:return:
			<bool>
				* True - EXR
				* False - PNG
		"""
		return self._explicit_to_exr

	@explicit_to_exr.setter
	def explicit_to_exr(self, value):
		self._explicit_to_exr = bool(value)

	@staticmethod
	def __cleanup_tex_arg(tex_arg, tex_name):
		"""
		Performs a pre-process for a texture argument.
		Ensures it's a list.

		:param tex_name: <string> name of the argument for errors.
		:return: <list>, for further conversion to tuple
		"""
		if tex_arg is None:
			tex_arg = list()
		elif isinstance(tex_arg, _str_t):
			tex_arg = [tex_arg]
		elif isinstance(tex_arg, set):
			tex_arg = list(sorted(tex_arg))
		elif hasattr(tex_arg, '__iter__') and not isinstance(tex_arg, list):
			tex_arg = list(tex_arg)

		return _err_comm.WrongTypeError(
			tex_arg, list, tex_name, 'tuple or list of strings'
		).raise_if_needed()

	@staticmethod
	def __get_tex_prop_val(val):
		"""
		:return:
			Resulting texture property value:
				* None - no textures specified
				* <string> - one texture
				* <tuple of strings> - multiple textures
		"""
		len_val = len(val)
		if len_val < 1:
			return None
		if len_val == 1:
			return val[0]
		return val

	def __set_src_tex(self, src_tex):
		"""
		Ensures self._src_tex is tuple of file paths, each exists and is readable.

		:param src_tex:
			<string or list/tuple of strings>
			Source texture(s).
		"""
		src_tex = self.__cleanup_tex_arg(src_tex, 'source texture')

		def check_single_item(item):
			item = _err_comm.NotStringError(
				item, 'source texture'
			).raise_if_needed_or_empty().replace('\\', '/')
			return _fl_error_check.file_readable(item)

		self._src_tex = tuple(
			(check_single_item(it) for it in src_tex)
		)

	@property
	def src_tex(self):
		"""
		:return:
			specified source texture(s):
				* None - no textures specified
				* <string> - one texture
				* <tuple of strings> - multiple textures
		"""
		return self.__get_tex_prop_val(self._src_tex)

	@src_tex.setter
	def src_tex(self, value):
		self.__set_src_tex(value)


	def __set_out_tex(self, out_tex):
		"""
		Ensures self._out_tex is tuple of file paths, with breadcrumbs as existing folders.

		:param out_tex:
			<string or list/tuple of strings>
			Output texture(s).
		"""
		out_tex = self.__cleanup_tex_arg(out_tex, 'out texture')

		def check_single_item(item):
			item = _err_comm.NotStringError(
				item, 'out texture'
			).raise_if_needed_or_empty().replace('\\', '/')
			return _fs.ensure_breadcrumbs_are_folders(item, 2)

		self._out_tex = tuple(
			(check_single_item(it) for it in out_tex)
		)

	@property
	def out_tex(self):
		"""
		:return:
			specified output texture(s):
				* None - no textures specified
				* <string> - one texture
				* <tuple of strings> - multiple textures
		"""
		return self.__get_tex_prop_val(self._out_tex)

	@out_tex.setter
	def out_tex(self, value):
		self.__set_out_tex(value)

	def get_out_tex(self):
		"""
		If present, the specified out_tex is returned.
		Otherwise, the resulting tex name(s) are generated from source texture(s).
		:return:
		"""
		out_tex = self.out_tex
		src = self._src_tex  # raw

		def _get_src_getter():
			"""
			Generates source texture getter - depending on the <out_tex> and <src> values.

			:return:
				<function> taking one argument (id in src tuple).
					* no source texture - NoPathError is raised
					* single source texture - it's always returned (regardless of provided id)
					*
						multiple source textures with single or no output -
						first source is always returned
					* multiple sources with multiple outputs - the source with given id is returned.
						*
							If there are more outputs then sources,
							**NoPathError** is raised at call with exceeding id.
			"""
			def _raiser(dummy_id):
				raise errors.NoPathError('source texture')

			if not src:
				return _raiser

			src_0 = src[0]
			first_src_f = lambda dummy_id: src_0

			if not(
				out_tex and
				isinstance(out_tex, tuple) and
				len(out_tex) > 1
			):
				# We have either None, empty string
				# or tuple with less than 2 items (single or empty).
				# Anyway, we need to always use 1st source input.
				if not(
					src_0 and isinstance(src_0, _str_t)
				):
					# ... but the actual 1st source is not provided.
					return _raiser
				return first_src_f

			# Now we're sure there are multiple outputs...

			len_src = len(src)
			if len_src == 1:  # we already took care of empty src ( == 0)
				# ... but only single input.
				return first_src_f

			# ... and there are multiple inputs, too
			# We need to provide individual source for each output.
			max_src_id = len_src - 1

			def _get_matching_src(src_id):
				if src_id > max_src_id:
					raise errors.NoPathError('source texture %s' % src_id)
				return src[src_id]

			return _get_matching_src

		get_src = _get_src_getter()
		assert callable(get_src)
