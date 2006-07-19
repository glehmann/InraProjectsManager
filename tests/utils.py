def dict_cmp(a, b):
	diff = {'+':[],'-':[],'!=':[]}
	for key in sorted(set(a.keys() + b.keys())):
		if (key not in a):
			diff['+'].append(key)
		elif (key not in b):
			diff['-'].append(key)
		elif a[key]!=b[key]:
			diff['!='].append(key)
	
	return diff
