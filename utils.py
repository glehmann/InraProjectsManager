
def labelFromId(self,id):
	""" cree un label a partir de l'id majuscule premiere lettre + minuscules et espaces a la place des _"""
	id = id[0].upper() + id[1:].lower()
	id = id.replace("_"," ")
	id = id.replace("ee","ée")
	return id

def normalizeSQL(self,fieldValue):
	""" returns a value adaptated to sql input
	returns none if null """
	if not(fieldValue):
		return None
	else:
		return fieldValue
