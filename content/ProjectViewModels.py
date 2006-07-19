from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

from Products.InraProjectsManager.interfaces import IProjectViewModel

def addProjectViewModel(self,id,REQUEST=None,**kwargs):
	""" adds an Inra View Model """
	object = ProjectViewModel(id,**kwargs)
	self._setObject(id, object)


class ProjectViewModel(ATFolder):
	""" contains information about the database table structure of a view, and its representation in the InraProjectsManager context :
	a dictionnary of the table structure
	a form - each field corresponding to a field of that table
	templates for displaying the view informations
	
	and tools to manage them
	"""
	
	__implements__ = (IProjectViewModel,)
	
	archetype_name="Project View Model"
	
	def getTableName(self):
		""" gets the database table name for this view """
		pass
	
	def getDbTableStructure(self,):
		""" returns a dictionnary of dictionnaries containing the structure of the table. :
			
		{str fieldName:{str: property:value}}
		
		properties are at least : label, width, type
		"""
		pass
	
	def setViewProperties(self,REQUEST=None):
		""" """
		pass
	
	def editViewProperties(self,REQUEST=None):
		""" """
		pass
	
	def createForm(self):
		""" creates the form from view properties """
		pass