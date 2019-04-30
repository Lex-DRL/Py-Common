"""
Abstract geometry math, not tied specifically to any 3D software.
"""

__author__ = 'Lex Darlog (DRL)'

try:
	# support type hints in Python 3:
	from typing import *
except ImportError:
	pass
from drl_common.py_2_3 import str_t

# TODO: https://gist.github.com/RedForty/9fc37bc8ad647256177c0749065ac262
import maya.cmds as cmds
import maya.api.OpenMaya as api


def bestFitPlane(points, plane=False):
	"""
	Takes an array of points (transforms)
	Returns a plane located at the centroid of the points
	It is oriented as a best fit plane using this method:
	http://www.ilikebigbits.com/blog/2017/9/24/fitting-a-plane-to-noisy-points-in-3d
	Optionally, you can feed it a plane and it will merely position and orient it
	"""
	if not points:  # Validate input
		return None

	pointPositions = {}
	for point in points:
		vector = api.MVector(cmds.xform(point, q=True, t=True, ws=True))
		pointPositions[point] = vector

	pointCount = 0
	averagePosition = api.MVector()
	for point in pointPositions.values():
		pointCount += 1
		averagePosition += point
	centroid = averagePosition / pointCount

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

	for point in pointPositions.values():
		r = point - centroid
		xx += r.x * r.x
		xy += r.x * r.y
		xz += r.x * r.z
		yy += r.y * r.y
		yz += r.y * r.z
		zz += r.z * r.z

	xx /= pointCount
	xy /= pointCount
	xz /= pointCount
	yy /= pointCount
	yz /= pointCount
	zz /= pointCount

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


# TO DO - Figure out how to flip the normal to face a specified direction. Ex. If the bone is on the other side.

# Select a bunch of locators/transforms
sel = cmds.ls(sl=1, fl=1)
bestFitPlane(sel)
