from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

from Products.InraProjectsManager.interfaces import IProjectView

from OFS.SimpleItem import SimpleItem

class ProjectView(SimpleItem):
	""" abstract class interface.
	a projectView subclass instance provides a view on an aspect of the project : project definition, ressources, reports, etc 
	each view type may have its particular class

	"""

	__implements__ = (IProjectView,)
	
	_on_public_form = False # true if fields for this view are used in the public form
	
	
	def getModel(self,):
		""" gets the model for this view, defined in the context of a InraProjectsManager instance 
		"""
		
		pass
	
	def getProjectViewId(self,):
		""" gets the identifiers (a tuple key, value) of that view of that project in the view table """
		
	def executeForm(self,**context):
		""" manages displaying, submission, validation, treatment of the form of that view in the context of this project. always returns XHTML code """

	def getTableName(self):
		""" gets the table of that view """
		pass
	
	def createDbEntry(self,fieldsValuesDictionary):
		""" feeds the table with datas from the public form """
		

class ProjectRequest(ProjectView):
		"""  provides a manager for the entry of contextual project in project requests table """
		_tableName = "project_requests"
		viewLabel = "project request"
		_on_public_form = True
		pass
	
class ProjectDiary(ProjectView):
		"""  provides a manager for the entry of contextual project in project diary table """		
		_tableName = "project_diaries"
		viewLabel = "project diary"
		
		pass
	
class ProjectTrainings(ProjectView):
		"""  provides a manager for the entry of contextual project in project trainings table """		
		_tableName = "project_trainings"
		viewLabel = "project trainings"
		
		pass
  
class ProjectUsers(ProjectView):
		"""  provides a manager for the entry of contextual project in project users table """		
		_tableName = "project_users"
		viewLabel = "project users"
		_on_public_form = "True"
		
		pass
	
class ProjectResults(ProjectView):
		"""  provides a manager for the entry of contextual project in project results table """		
		_tableName = "project_results"
		viewLabel = "project results"
		
		pass

class ProjectRessources(ProjectView):
		""" provides a manager for the entry of contextual project in project ressources table """		
		_tableName = "project_ressources"
		viewLabel = "project ressources"
		
		pass

  
def getProjectViewsList():
	""" returns the list of classes that manages a view """
	viewClassesList = []
	this_module = globals()
	for objet in this_module.values():
		# duck test
		#viewClassesList.append(objet)
		if hasattr(objet,"viewLabel") and hasattr(objet,"__implements__"):
			if IProjectView in objet.__implements__:
				viewClassesList.append(objet)
		
	return viewClassesList
		
def getProjectViewsNames():
	""" returns the list of view names managed by this version """
	return [objet.viewLabel for objet in getProjectViewsList()]