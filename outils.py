# -*- encoding: utf-8 -*-
from Products.Formulator import Form

def labelFromId(id):
	""" cree un label a partir de l'id majuscule premiere lettre + minuscules et espaces a la place des _"""
	id = Form.convert_unicode(id)
	id = id.replace("_"," ")
	id = id[0].upper() + id[1:].lower()
	return id.strip()

def normalizeSQL(fieldValue):
	""" returns a value adaptated to sql input
	returns none if null """
	if not(fieldValue):
		return None
	else:
		return fieldValue

def dict_cmp(a, b):
	diff = []
	for key in sorted(set(a.keys() + b.keys())):
		if (key not in a):
			diff.append(key)
		elif (key not in b):
			diff.append(key)
		elif a[key]!=b[key]:
			diff.append(key)
	
	return diff
		
		
def same_type(a,b):
	return type(a)==type(b)