"""
Abstract geometry math, not tied specifically to any 3D software.
"""

__author__ = 'Lex Darlog (DRL)'

# noinspection PyProtectedMember
from .utils import (
	flatten_gen as _flatten,
	_Iterable,
	_Iterator
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


def vector3_gen(*components):
	"""
	Generator that always produces a sequence of exactly 3 float/int elements.
	It's kinda a slice, but works even if the original iterable
	doesn't support slicing, and also fills missing components with zeroes.
	"""

	i = 0  # after the loop, it will have the num of sent components
	# loop over given components, but only up to the 3rd:
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

		if not isinstance(comp, (int, float)):
			continue
		if i > 2:
			break
		yield comp
		i += 1
	# if we sent less then 3, fill the remaining ones with zero:
	for x in xrange(3 - i):
		yield 0


def points_closest_plane(
	positions  # type: _t.Sequence[api.MVector]
):
	"""
	https://gist.github.com/RedForty/9fc37bc8ad647256177c0749065ac262

	Takes an array of points (transforms)
	Returns a plane located at the centroid of the points
	It is oriented as a best fit plane using this method:
	http://www.ilikebigbits.com/blog/2017/9/24/fitting-a-plane-to-noisy-points-in-3d
	Optionally, you can feed it a plane and it will merely position and orient it
	"""
	if not positions:  # Validate input
		return None

	if __is_maya:
		from maya import cmds
		from maya.api import OpenMaya as api
		from pymel import core as pm
		from drl.for_maya.ls.convert import components as comp

	def cleanup_pos_as_maya(iterable):
		"""
		A generator that turns whatever input is given
		to an iterable of MVector items.

		Supported inputs are:
			* the actual MVectors
			* components given either as PyNode objects or as a cmds's style strings.

		Anything else is simply filtered out.
		"""
		def _process_comps(comps):
			"""
			A generator, converting a given comp(s) to vertices
			and then reading their positions.
			"""
			comps = (c for c in comps if isinstance(c, pm.Component))
			verts = set(
				comp.Poly(comps, selection_if_none=False).to_vertices(flatten=True)
			)
			for v in verts:
				pos_comps = pm.xform(v, q=True, t=True, ws=True)  # type: _t.List[float]
				# noinspection PyArgumentList
				yield api.MVector(pos_comps)

		# we may have a single item, which corresponds to multiple vertices:
		if isinstance(iterable, _str_t) or isinstance(iterable, pm.Component):
			for vector in _process_comps(pm.ls(iterable)):
				yield vector
				return

		if not isinstance(iterable, (_Iterable, _Iterator)):
			# we've got a single item and it can't represent multiple points
			return

		for pos in iterable:
			if isinstance(pos, api.MVector):
				yield pos
				continue

			if isinstance(pos, _str_t) or isinstance(pos, pm.Component):
				for vector in _process_comps(pm.ls(pos)):
					yield vector
				continue

			if isinstance(pos, (_Iterable, _Iterator)):
				px, py, pz = vector3_gen(pos)
				# noinspection PyArgumentList
				yield api.MVector(px, py, pz)

	positions = list(positions)

	num_p = len(positions)
	averagePosition = api.MVector()
	for point in positions:
		averagePosition += point
	centroid = averagePosition / num_p

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

	weighted_dir = api.MVector()

	# X
	det_x = yy * zz - yz * yz
	axis_dir = api.MVector(det_x, (xz * yz - xy * zz), (xy * yz - xz * yy))
	weight = det_x * det_x
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	# Y
	det_y = xx * zz - xz * xz
	axis_dir = api.MVector((xz * yz - xy * zz), (det_y), (xy * xz - yz * xx))
	weight = det_y * det_y
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	# Z
	det_z = xx * yy - xy * xy
	axis_dir = api.MVector((xy * yz - xz * yy), (xy * xz - yz * xx), (det_z))
	weight = det_z * det_z
	if (weighted_dir * axis_dir) < 0.0:
		weight = -weight
	weighted_dir += axis_dir * weight

	normal = weighted_dir.normalize()

	angle = cmds.angleBetween(euler=True, v1=(0, 1, 0), v2=normal)  # Y is the 'up' or 'normal' axis
	plane = cmds.polyPlane(name='bestFitPlane', width=10, height=10, sx=1, sy=1)
	cmds.xform(plane, ro=angle, t=centroid)
	return plane
