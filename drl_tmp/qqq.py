from collections import defaultdict
d = defaultdict(list)
d.keys()
d['aaa'].append(123)

grp = {}
grp['aaa'] = 123
grp.keys()


from drl_py23 import reload
d = {str(x): x for x in range(7)}
