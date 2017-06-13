__author__ = 'DRL'


from os import path as _os_path
from os import getenv as _os_getenv

from drl_common import errors as _err_comm
from drl_common import filesystem as _fs

from . import defaults as _def
from . import envs as _env
from . import errors as _err

_str_types = (str, unicode)


class NukeProcessor(object):
	def __init__(
		self,
		src_tex, out_tex=None, explicit_to_exr=True,
		nk_dir='', nk_file='',
		py_dir='', py_file='',
		nuke_dir='', nuke_exe='',
		home_override_env=_env.NUKE_HOME_OVERRIDE
	):
		super(NukeProcessor, self).__init__()

		self.__src_tex = tuple()
		self.__out_tex = tuple()
		self.__explicit_to_exr = bool(explicit_to_exr)

		self.__nuke_dir = ''
		self.__nuke_exe = ''
		
		self.__nk_dir = ''
		self.__nk_file = ''
		self.__py_dir = ''
		self.__py_file = ''
		self.__home_override_env = ''

		self.__set_src_tex(src_tex)
		self.__set_out_tex(out_tex)

		self.__set_nuke_dir(nuke_dir)
		self.__set_nuke_file(nuke_exe)
		self.__set_nk_dir(nk_dir)
		self.__set_nk_file(nk_file)
		self.__set_py_dir(py_dir)
		self.__set_py_file(py_file)
		self.__set_home_env_override(home_override_env)


# region Low-level Dir-File property setters
	
	@staticmethod
	def __get_default_value(env_nm=None, def_val=None):
		if not(env_nm and isinstance(env_nm, _str_types)):
			return def_val
		return _os_getenv(env_nm, def_val)

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


	def __set_nuke_dir(self, path):
		self.__nuke_dir = NukeProcessor.__get_dir_value(
			path, _env.NUKE_DIR, _def.nuke_dir, NukeProcessor.__to_windows, _err.nuke_dir
		)

	def __set_nuke_file(self, file_name):
		self.__nuke_exe = NukeProcessor.__get_file_value(
			self.__nuke_dir, file_name, _env.NUKE_EXE, _def.nuke_exe,
			NukeProcessor.__to_windows, _err.nuke_exe
		)
	
	def __set_nk_dir(self, path):
		self.__nk_dir = NukeProcessor.__get_dir_value(
			path, _env.NK_DIR, _def.nk_dir, NukeProcessor.__to_unix, _err.nk_dir
		)

	def __set_nk_file(self, file_name):
		self.__nk_file = NukeProcessor.__get_file_value(
			self.__nk_dir, file_name, None, _def.nk_file,
			NukeProcessor.__to_unix, _err.nk_file
		)

	def __set_py_dir(self, path):
		self.__py_dir = NukeProcessor.__get_dir_value(
			path, _env.PY_DIR, _def.py_dir, NukeProcessor.__to_windows, _err.py_dir
		)

	def __set_py_file(self, file_name):
		self.__py_file = NukeProcessor.__get_file_value(
			self.__py_dir, file_name, None, _def.py_file,
			NukeProcessor.__to_windows, _err.py_file
		)

	def __set_home_env_override(self, env_name):
		if not env_name:
			self.__home_override_env = ''
			return

		env_name = _err_comm.NotStringError(env_name, 'env_name').raise_if_needed()
		self.__home_override_env = env_name

# endregion


# region Dir-File properties
	
	@property
	def nuke_dir(self):
		return self.__nuke_dir

	@nuke_dir.setter
	def nuke_dir(self, value):
		self.__set_nuke_dir(value)

	@property
	def nuke_exe(self):
		return self.__nuke_exe

	@nuke_exe.setter
	def nuke_exe(self, value):
		self.__set_nuke_file(value)

	@property
	def nk_dir(self):
		return self.__nk_dir

	@nk_dir.setter
	def nk_dir(self, value):
		self.__set_nk_dir(value)

	@property
	def nk_file(self):
		return self.__nk_file

	@nk_file.setter
	def nk_file(self, value):
		self.__set_nk_file(value)

	@property
	def py_dir(self):
		return self.__py_dir

	@py_dir.setter
	def py_dir(self, value):
		self.__set_py_dir(value)

	@property
	def py_file(self):
		return self.__py_file

	@py_file.setter
	def py_file(self, value):
		self.__set_py_file(value)

	@property
	def home_override_env(self):
		return self.__home_override_env

	@home_override_env.setter
	def home_override_env(self, value):
		self.__set_home_env_override(value)

# endregion

# region Full path getters

	def nuke_exe_path(self):
		"""
		Get the actual path of nuke.exe file, ready to be passed to the command line.

		:return: <str>
		"""
		return NukeProcessor.__to_windows(
			self.__nuke_dir + '/' + self.__nuke_exe,
			as_file=True
		)

	def nk_file_path(self):
		"""
		Get the actual path to the nk script file, ready to be passed to the command line.

		:return: <str>
		"""
		return NukeProcessor.__to_unix(
			self.__nk_dir + '/' + self.__nk_file,
			as_file=True
		)

	def py_file_path(self):
		"""
		Get the actual path of python file that launches the render,
		ready to be passed to the command line.

		:return: <str>
		"""
		return NukeProcessor.__to_windows(
			self.__py_dir + '/' + self.__py_file,
			as_file=True
		)

# endregion


# region Low-level Texture property setters-getters
	
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
		Ensures self.__src_tex is tuple of file paths, each exists and is readable.

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

		self.__src_tex = tuple(
			(check_single_item(it) for it in src_tex)
		)

	def __set_out_tex(self, out_tex):
		"""
		Ensures self.__out_tex is tuple of file paths, with breadcrumbs as existing folders.

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

		self.__out_tex = tuple(
			(check_single_item(it) for it in out_tex)
		)
		
# endregion


# region Texture Properties

	@property
	def src_tex(self):
		"""
		:return:
			specified source texture(s):
				* None - no textures specified
				* <string> - one texture
				* <tuple of strings> - multiple textures
		"""
		return self.__get_tex_prop_val(self.__src_tex)

	@src_tex.setter
	def src_tex(self, value):
		self.__set_src_tex(value)


	@property
	def out_tex(self):
		"""
		:return:
			specified output texture(s):
				* None - no textures specified
				* <string> - one texture
				* <tuple of strings> - multiple textures
		"""
		return self.__get_tex_prop_val(self.__out_tex)

	@out_tex.setter
	def out_tex(self, value):
		self.__set_out_tex(value)

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
		return self.__explicit_to_exr

	@explicit_to_exr.setter
	def explicit_to_exr(self, value):
		self.__explicit_to_exr = bool(value)

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
		out = self.__out_tex
		src = self.__src_tex
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
				raise _err.NoPathError('source texture')

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
				src_err = _err.NoPathError('source texture %s' % src_id)
				if src_id > max_src_id:
					raise src_err
				res_src = src[src_id]
				if not (isinstance(res_src, _str_types) and res_src):
					raise src_err
				return res_src

			return _get_matching_src

		get_src = _get_src_getter()
		assert callable(get_src)

		gen_ext = '.exr' if self.__explicit_to_exr else '.png'

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

# endregion

	def get_command(self, nuke_x=False):
		"""
		Generates the command string that actually launches Nuke.

		It contains these parts:
			* "C:\Program Files\Nuke8.0v5\Nuke8.0.exe" // path to the nuke.exe
			*
				-t "e:\1-Projects\0-Scripts\Python\for_nuke\process_with_script.py"
				// the script opening the scene and launching render process
			*
				"e:/1-Projects/0-Scripts/Python/for_nuke/post-bake_turtle_unity.nk"
				// the actual nuke script file (it's passed as the 1st argument to a py script)
			*
				"('y:/in_tex_A.png', 'y:/in_tex_B.exr')"
				// the input texture(s) represented as a string,
				so the py script will get the same data by performing eval() on this argument.
			*
				"'y:/out_tex.png'"
				// similarly, the output texture

		:return: <string>
		"""
		nuke_exe_path = self.nuke_exe_path()
		if '"' in nuke_exe_path:
			raise _err.nuke_exe_with_quotes

		py_path = self.py_file_path()
		if '"' in py_path:
			raise _err.py_file_with_quotes

		nk_path = self.nk_file_path()
		if '"' in nk_path:
			raise _err.nk_file_with_quotes

		src_tex_arg = repr(str(self.src_tex))
		if not src_tex_arg:
			src_tex_arg = '""'
		if not src_tex_arg[0] == '"':
			src_tex_arg = '"%s"' % src_tex_arg

		out_tex_arg = repr(str(self.get_out_tex()))
		if not out_tex_arg:
			out_tex_arg = '""'
		if not out_tex_arg[0] == '"':
			out_tex_arg = '"%s"' % out_tex_arg

		return '"{nuke}" {nukex} -t "{py}" "{nk}" {src} {out}'.format(
			nuke=nuke_exe_path,
			nukex='--nukex' if nuke_x else '',
			py=py_path,
			nk=nk_path,
			src=src_tex_arg,
			out=out_tex_arg
		)

	# TODO: start the actual render-starter class (the one that's called from py script)