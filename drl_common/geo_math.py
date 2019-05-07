"""
Abstract geometry math, not tied specifically to any 3D software.
"""

__author__ = 'Lex Darlog (DRL)'

from .utils import flatten_gen as _flatten
from collections import (
	Iterable as _Iterable,
	Iterator as _Iterator
)

try:
	# support type hints in Python 3:
	# noinspection PyUnresolvedReferences
	import typing as _t
except ImportError:
	pass
from drl_common.py_2_3 import (
	str_t as _str_t,
	str_hint as _str_hint
)

__is_maya = False
try:
	# noinspection PyUnresolvedReferences
	from .is_maya import is_maya as _is_maya_f
	__is_maya = _is_maya_f()
except ImportError:
	pass


def vector_gen(components, size=3):
	"""
	Generator that always produces a sequence of `size`, containing float/int elements.
	It's kinda a slice, but works even if the original iterable
	doesn't support slicing, and also fills missing components with zeroes.
	"""
	size = max(1, size)
	max_index = size - 1

	i = 0  # after the loop, it will have the num of sent components

	# loop over given components, but only up to the Nth:
	for comp in _flatten(components):
		if isinstance(comp, _str_t):
			# the comp is a string. Let's try to extract a float/int from it:
			try:
				comp = int(comp)
			except ValueError:
				try:
					comp = float(comp)
				except ValueError:
					pass

		if i > max_index:
			break
		if not isinstance(comp, (int, float)):
			continue

		yield comp
		i += 1
	# if we sent less then 3, fill the remaining ones with zero:
	for x in xrange(size - i):
		yield 0


def __closest_plane_maya(
	positions  # type: _t.Sequence[_t.Sequence]
):
	"""
	https://gist.github.com/RedForty/9fc37bc8ad647256177c0749065ac262

	Takes an array of points (transforms)
	Returns a plane located at the centroid of the points
	It is oriented as a best fit plane using this method:
	http://www.ilikebigbits.com/blog/2017/9/24/fitting-a-plane-to-noisy-points-in-3d
	Optionally, you can feed it a plane and it will merely position and orient it
	"""
	from maya import cmds
	# noinspection PyPep8Naming
	from maya.api import OpenMaya as api
	from pymel import core as pm
	from drl.for_maya.ls.convert import components as comp

	# noinspection PyPep8Naming
	def vector(*vector_comps):
		"""
		A wrapper which only purpose is to suppress PyCharm warnings
		caused by shitty Maya devkit which makes PyCharm think that
		any argument list is wrong.

		Hallelujah Autodesk!
		Or, more precisely, Seig Heil Auto-Fucking-Desk!
		"""
		# noinspection PyArgumentList
		return api.MVector(*vector_comps)

	def cleanup_pos(iterable):
		"""
		A generator that turns whatever input is given
		to an iterable of MVector items.

		Supported inputs are:
			* the actual MVectors
			* components given either as PyNode objects or as a cmds's style strings.

		Anything else is simply filtered out.
		"""
		def _comps_to_positions(comps):
			"""
			A generator, converting a given comp(s) to vertices
			and then - to their positions.
			"""
			comps = (c for c in comps if isinstance(c, pm.Component))
			verts = set(
				comp.Poly(comps, selection_if_none=False).to_vertices(flatten=True)
			)
			for vtx in verts:
				pos_comps = pm.xform(vtx, q=True, t=True, ws=True)  # type: _t.List[float]
				yield vector(pos_comps)

		# we may have a single item, which corresponds to multiple vertices:
		if isinstance(iterable, _str_t) or isinstance(iterable, pm.PyNode):
			iterable = pm.ls(iterable)  # no need to flatten, we'll do it in converting func
			for vec in _comps_to_positions(pm.ls(iterable)):
				yield vec
			return

		if isinstance(iterable, (api.MVector, api.MFloatVector)):
			# to avoid iterating over a single vector's components:
			return

		# let's check if it's an iterable by brute-forcefully attempting
		# to actually iterate over it:
		try:
			iterable = iter(iterable)
		except TypeError:
			# we've got a single value (not an iterable)
			# that can't even be converted to vertices. So just finish:
			return

		for pos in iterable:
			if isinstance(pos, api.MFloatVector):
				yield vector(pos)
				continue
			if isinstance(pos, api.MVector):
				yield pos
				continue

			if isinstance(pos, _str_t) or isinstance(pos, pm.Component):
				for vec in _comps_to_positions(pm.ls(pos)):
					yield vec
				continue

			try:
				pos = iter(pos)
			except TypeError:
				continue

			yield vector(vector_gen(pos))

	positions = list(cleanup_pos(positions))

	num_p = len(positions)
	average_pos = vector()
	for point in positions:
		average_pos += point
	centroid = vector(average_pos / float(num_p))

	# loc = 'derp'
	# loc = cmds.spaceLocator(n='derp', a=True)
	# cmds.xform(loc, t=centroid)

	# Calculate full 3x3 covariance matrix, excluding symmetries
	xx = 0.0
	xy = 0.0
	xz = 0.0
	yy = 0.0
	yz = 0.0
	zz = 0.0

	for point in positions:
		r = point - centroid
		xx += r.x * r.x
		xy += r.x * r.y
		xz += r.x * r.z
		yy += r.y * r.y
		yz += r.y * r.z
		zz += r.z * r.z

	xx /= num_p
	xy /= num_p
	xz /= num_p
	yy /= num_p
	yz /= num_p
	zz /= num_p

	weighted_dir = vector()

	# X
	det_x = yy * zz - yz * yz
	axis_dir = vector(
		det_x,
		(xz * yz - xy * zz),
		(xy * yz - xz * yy)
	)
	weight = det_x * det_x
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	# Y
	det_y = xx * zz - xz * xz
	axis_dir = vector((xz * yz - xy * zz), (det_y), (xy * xz - yz * xx))
	weight = det_y * det_y
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	# Z
	det_z = xx * yy - xy * xy
	axis_dir = vector((xy * yz - xz * yy), (xy * xz - yz * xx), (det_z))
	weight = det_z * det_z
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	normal = weighted_dir.normalize()

	angle = cmds.angleBetween(euler=True, v1=(0, 1, 0), v2=normal)  # Y is the 'up' or 'normal' axis
	plane = cmds.polyPlane(name='bestFitPlane', width=10, height=10, sx=1, sy=1)
	cmds.xform(plane, ro=angle, t=centroid)
	return plane


def __closest_plane_numpy(
	positions  # type: _t.Sequence[_t.Sequence]
):
	try:
		import numpy as np
	except ImportError:
		import modules as _mdl
		_mdl.pip_install('numpy', upgrade=False)
		import numpy as np
	# TODO: non-maya function, using numpy


def points_closest_plane(
	positions  # type: _t.Sequence[_t.Sequence]
):
	# just early exit if positions is either a string or not a meaningful sequence:
	if isinstance(positions, _str_t) or not(
		positions and
		isinstance(positions, (_Iterable, _Iterator))
	):  # Validate input
		return None

	if __is_maya:
		return __closest_plane_maya(positions)
	else:
		return __closest_plane_numpy(positions)
