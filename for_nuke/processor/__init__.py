__author__ = 'DRL'


from os import path as _os_path, getenv

from drl_common import errors as _err_comm
from drl_common import filesystem as _fs

from . import defaults, envs, errors

_str_types = (str, unicode)

err_nk_dir = errors.NoPathError('nk-script directory')
err_nk_file = errors.NoPathError('nk-script', is_file=True)


class NukeProcessor(object):
	def __init__(
		self,
		src_tex, out_tex=None, explicit_to_exr=True,
		nk_dir='', nk_file='',
		py_dir='', py_file='',
		nuke_dir='', nuke_exe='',
		home_override_env='DRL_NUKE_HOME'
	):
		super(NukeProcessor, self).__init__()

		self._src_tex = tuple()
		self._out_tex = tuple()
		self._explicit_to_exr = bool(explicit_to_exr)

		self._nk_dir = ''
		self._nk_file = ''
		self._py_dir = ''
		self._py_file = ''
		self._nuke_dir = ''
		self._nuke_file = ''


		self.__set_src_tex(src_tex)
		self.__set_out_tex(out_tex)

		# TODO
		self.__set_nk_dir(nk_dir)
		self.__set_nk_file(nk_file)


	@staticmethod
	def __get_default_value(env_nm=None, def_val=None):
		if not(env_nm and isinstance(env_nm, _str_types)):
			return def_val
		return getenv(env_nm, def_val)

	@staticmethod
	def __to_unix(path, as_file=False):
		"""
		Convert slashes to **unix**-style. Trailing slashes are removed.

		:param path: <string>
		:param as_file: <bool> when True, leading slashes are removed, too.
		:return: <string>
		"""
		assert isinstance(path, _str_types)
		path = path.replace('\\', '/').rstrip('/')
		if as_file:
			path = path.lstrip('/')
		return path

	@staticmethod
	def __to_windows(path, as_file=False):
		"""
		Convert slashes to **win**-style. Trailing slashes are removed.

		:param path: <string>
		:param as_file: <bool> when True, leading slashes are removed, too.
		:return: <string>
		"""
		path = path.replace('/', '\\').rstrip('\\')
		if as_file:
			path = path.lstrip('\\')
		return path

	@staticmethod
	def __get_dir_value(path, env, default, slash_converter_f, error):
		"""
		Get directory value, with fallback to the env-var (if present)
		and then to default value.

		The given path is checked for existence and being a folder.

		Slashes are converted to the specified format, with trailing slash removed.

		:param path: <string/None> the given value for a directory.
		:param env: <string/None> env-var name to check if no value given.
		:param default: <string> default value if no env-var given.
		:param slash_converter_f: either **__to_unix** or **__to_windows**
		:param error: the <error object> to raise if folder doesn't exist.
		:return: <string>
		"""
		if not(
			path and isinstance(path, _str_types)
		):
			path = NukeProcessor.__get_default_value(env, default)

		path = _os_path.abspath(path)
		path = slash_converter_f(path)
		if not(
			_os_path.exists(path) and _os_path.isdir(path)
		):
			raise error

		return path

	@staticmethod
	def __get_file_value(parent_dir, file_nm, env, default, slash_converter_f, error):
		"""
		Get file value, with fallback to the env-var (if present)
		and then to default value.

		First, parent path is checked for being existing folder.
		Then, given filename/sub-path is checked for existence and being a file.

		Slashes are converted to the specified format, with trailing slash removed.

		:param parent_dir: <string> path to the parent folder
		:param file_nm: <string/None> the given value for a file.
		:param env: <string/None> env-var name to check if no value given.
		:param default: <string> default value if no env-var given.
		:param slash_converter_f: either **__to_unix** or **__to_windows**
		:param error: the <error object> to raise if folder doesn't exist.
		:return: <string>
		"""
		if not(
			parent_dir and isinstance(parent_dir, _str_types) and
			_os_path.exists(parent_dir) and _os_path.isdir(parent_dir)
		):
			raise error

		if not(
			file_nm and isinstance(file_nm, _str_types)
		):
			file_nm = NukeProcessor.__get_default_value(env, default)

		file_nm = slash_converter_f(file_nm, as_file=True)
		combined = slash_converter_f(parent_dir) + '/' + file_nm
		if not(
			_os_path.exists(combined) and _os_path.isfile(combined)
		):
			raise error

		return file_nm


	def __set_nk_dir(self, nk_dir):
		self._nk_dir = NukeProcessor.__get_dir_value(
			nk_dir, envs.NK_DIR, defaults.nk_dir, NukeProcessor.__to_windows, err_nk_dir
		)

	def __set_nk_file(self, nk_file):
		self._nk_file = NukeProcessor.__get_file_value(
			self._nk_dir, nk_file, None, defaults.nk_file,
			NukeProcessor.__to_windows, err_nk_file
		)

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
		elif isinstance(tex_arg, _str_types):
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
			return _fs.error_if.path_not_readable(item)

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
			if not item:
				return None
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
		Generate the file path(s), ready to be passed to the nuke script as an argument.

		* If no **out_tex** specified, a single filename generated from source file.
		* If single out tex specified, it's returned as string.
		* If multiple output textures given, they're returned as a tuple.
		*
			In multi-output case, if any out item is **None** or **empty string**,
			the corresponding out-tex is generated from source tex.

		When file names are generated, they're guaranteed to be unique
		(file with this name don't exist yet). '_' prefix is added if necessary.

		When file names specified explicitly, it's your responsibility to check them.

		:return:
			The full path for the output texture.
				* <str> If no or single out-file provided.
				* <tuple of str> for multiple outputs.
		"""
		out = self._out_tex
		src = self._src_tex
		assert isinstance(out, tuple)
		assert isinstance(src, tuple)
		len_src = len(src)
		len_out = len(out)

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

			if len_out < 2:
				# We have single or no outputs.
				# Anyway, we need to always use 1st source input.
				if not(
					src_0 and isinstance(src_0, _str_types)
				):
					# ... but the actual 1st source is not provided.
					return _raiser
				return first_src_f

			# Now we're sure there are multiple outputs...

			if len_src == 1:  # we already took care of empty src ( == 0)
				# ... but only single input.
				return first_src_f

			# ... and there are multiple inputs, too
			# We need to provide individual source for each output.
			max_src_id = len_src - 1

			def _get_matching_src(src_id):
				src_err = errors.NoPathError('source texture %s' % src_id)
				if src_id > max_src_id:
					raise src_err
				res_src = src[src_id]
				if not (isinstance(res_src, _str_types) and res_src):
					raise src_err
				return res_src

			return _get_matching_src

		get_src = _get_src_getter()
		assert callable(get_src)

		gen_ext = '.exr' if self._explicit_to_exr else '.png'

		def gen_from_src(idx, planned_files=None):
			"""
			Generate the actual output file from source, that doesn't exist on disk.

			:param idx: id of source file
			:param planned_files:
				<set, optional>
				If specified, the function adds '_' to the base filename
				until it finds the filename that's not taken yet.
			:return: <string>
			"""
			if not planned_files:
				planned_files = set()
			planned_files = set(x.lower().replace('\\', '/') for x in planned_files)

			cur_src = get_src(idx)
			assert isinstance(cur_src, _str_types)
			cur_lower = cur_src.lower()
			planned_files.add(cur_lower)

			base, ext = _os_path.splitext(cur_src)
			ext = gen_ext.lower()

			def _base_needs_to_be_extended(src_base, src_ext):
				"""
				Whether the filename is already taken, so it needs to be extended once again.
				"""
				combined = (src_base + src_ext).lower().replace('\\', '/')
				if combined in planned_files:
					return True
				if _os_path.exists(combined):
					return True
				return False

			while _base_needs_to_be_extended(base, ext):
				base += '_'

			return base + ext

		def to_full_path(short_path):
			return _os_path.abspath(short_path).replace('\\', '/')


		if not out:
			# no output given - return source:
			return to_full_path(gen_from_src(0))
		if len_out == 1:
			# one output given - return single result:
			out_0 = out[0]
			if out_0 and isinstance(out_0, _str_types):
				return to_full_path(out_0)
			return to_full_path(gen_from_src(0))

		taken_file_paths = set()

		def process_single(i, itm):
			if not(itm and isinstance(itm, _str_types)):
				itm = gen_from_src(i, taken_file_paths)
			taken_file_paths.add(itm)
			return to_full_path(itm)

		return tuple(
			(process_single(i, it) for i, it in enumerate(out))
		)