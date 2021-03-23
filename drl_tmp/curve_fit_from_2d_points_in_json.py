import math

from drl_py23 import (
	xrange as _xrange,
)


def func_with_10_octaves(x):
	a, b, c, d = (
		0.4480124899561852,
		5.042099677369214,
		-0.7804122938274592,
		0.3683336353647238,
	)
	return a * math.exp(b * (x + c)) + d


def find_curve_fit():
	"""
	This func should be used to detect the actual coefficients.
	It should be done from a full-featured python, with scientific modules installed.
	"""

	try:
		# support type hints in Python 3:
		# noinspection PyUnresolvedReferences
		import typing as _t
	except ImportError:
		pass

	import json
	import numpy as np
	from matplotlib import pyplot as plt
	from scipy.optimize import curve_fit
	from pprint import pprint as pp

	json_path = r'P:\Projects\_Grass\1-cache\CalcNoisePeaks.json'

	with open(json_path, "r") as json_file:
		points = json.load(json_file)

	points = [tuple(p[:2]) for p in points]
	# pp(points[:20])
	len(points)


	def func_np(x, a, b, c, d):
		return a * np.exp(b*(x + c)) + d


	def func_math(x, a, b, c, d):
		return a * math.exp(b * (x + c)) + d


	xs, ys = zip(*points)
	xs = np.array(xs)  # type: np.ndarray
	ys = np.array(ys)  # type: np.ndarray
	print(xs.shape, ys.shape, len(points))

	init_guess = [1.0, 1.0, 0.0, 0.0]
	guess, covars = curve_fit(func_np, xs, ys, init_guess)

	n = 100
	step = 1.0 / n
	guessed_x = np.array([i * step for i in _xrange(1, n + 1)])
	guessed_y = np.array([func_np(x, *guess) for x in guessed_x])

	# check that np and math funcs output the same result:
	# guessed_y2 = np.array([func_math(x, *guess) for x in guessed_x])
	# deltas = [a1 - a2 for a1, a2 in zip(guessed_y, guessed_y2)]
	# sorted(deltas, reverse=True)

	plt.plot(xs, ys, 'bo', label='experimental data')
	plt.plot(guessed_x, guessed_y, label='guess')

	# i = 3
	# cov = covars[i]
	# cov_y = np.array([func(x, *cov) for x in guessed_x])
	# plt.plot(guessed_x, cov_y, label='covar ' + str(i))

	plt.show()

	guess_lst = list(guess)
	# [0.4480124899561852, 5.042099677369214, -0.7804122938274592, 0.3683336353647238]

	step = 0.05
	cur_v = step
	while cur_v < 1:
		print('{} -> {}'.format(math.exp(cur_v), np.exp(cur_v)))
		cur_v += step
