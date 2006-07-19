from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList

from Products.InraProjectsManager.interfaces import IInraProject


def addInraProject(self,id,REQUEST=None,**kwargs):
	""" adds an Inra Projects Manager """
	object = InraProject(id,**kwargs)
	self._setObject(id, object)


class InraProject(ATFolder):
	""" Provides an object that manages a project """
	__implements__ = ATFolder.__implements__ + (IInraProject,)
	""" Provides an object that manages a project """
	
	archetype_name = "Inra Project"
	
	def getState(self):
		""" the state of the project : , working, refused, aborted, finished"""
	def getLife(self):
		""" the state of the project document : live, archive, test or trash """
	
	def getConfidentiality(self):
		""" the confidentiality level : public, inra, confidential"""
	
	def getProjectDbKey(self,):
		""" gets the identifier of that project in the database """
	
	def createViews(self,):
		""" creates the views of the project """
		pass
	
	def getView(self,viewNameStr):
		""" gets the view viewNameStr """
		pass
	
	
registerType(InraProject)