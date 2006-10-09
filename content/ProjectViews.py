from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod

from Products.InraProjectsManager.interfaces import IProjectView
from Products.InraProjectsManager.config import *

from OFS.SimpleItem import SimpleItem
from Acquisition import Implicit
from OFS.Folder import Folder
	
class ProjectView(SimpleItem):
	""" abstract class.
	a projectView subclass instance provides a view on an aspect of the project : project definition, ressources, reports, etc 
	each view type may have its particular class
	"""

	__implements__ = (IProjectView,)
	
	_on_public_form = False # true if fields for this view are used in the public form	
	
	_view_main_template_layer_name = CANONICAL_VIEW_MAIN_TEMPLATE # the layer (in InraProjectsManager skin) name to be used at view main display. should be adaptated to each view
	
	
	_main_select_request_ZSQLFile = CANONICAL_VIEW_MAIN_SELECT_REQUEST_ZSQLFile # the select request to be used at view main display. may be adaptated to each view
	_FirstAddRequestFile = CANONICAL_FIRST_VIEW_ADD_ZSQLFile # the request to be used when a project is created from public form	
	_main_add_request_ZSQLFile = CANONICAL_VIEW_MAIN_ADD_REQUEST_ZSQLFile # the add request to be used at main view form submission (to add an entry about a project's view)
	
	_report_request_ZSQLFile = CANONICAL_REPORT_REQUEST_ZSQLFile # the request to be used when a view is asked for a report
	
	_deleteCache = True
	
	_historicisedReport = False # if true, all entries are displayed on reports (RessourceView for example)
					# <=> all entries of report_request are displayed
					# if false, only the last one is displayed (ResultsView for example)
					
	def getId(self):
		""" """
		return self.__class__.__name__
	
	def getModel(self,):
		""" gets the model for this view, defined in the context of a InraProjectsManager instance 
		"""
		
		return self.models.getModel(self.getId())[0]
		pass
	

	def executeForm(self,**context):
		""" manages displaying, submission, validation, treatment of the form of that view in the context of this project. always returns XHTML code """
	
		
	# ####### VIEW PROPERTIES
	
	def getTableName(self):
		""" gets the table of that view """
		try:
			return self._tableName
		except KeyError:
			raise KeyError, "abstract ProjectView class doesn't have tableName property"
		
		pass
	
	def getName(self):
		return self.__class__.__name__
	
	def getTablePkey(self):
		""" gets the table of that view """
		try:
			return self._table_pkey
		except KeyError:
			raise KeyError, "abstract ProjectView class doesn't have pkey property"
		
		pass
	
  	def getViewTitle(self):
		""" gets view title which is model's one """
		return self.getModel().title
	
	def getViewDescription(self):
		""" """
		return self.view_description
	
	# ################ DISPLAYING RELATED METHODS
	
	def getView_main_template_name(self):
		return self._view_main_template_layer_name
	
	_main_select=None
	def getMainSelectRequest(self):
		""" gets the main select request, from _main_select_request_ZSQLFile """
		if not self._main_select:
			self._main_select = FSZSQLMethod(self,self._main_select_request_ZSQLFile)
			self._main_select.connection = self.connection
		return self._main_select
		
	def getUserFieldsIds(self):
		""" returns the ids of the user-defined fields """
		return self.getModel().getUserFieldsIds()
	
	def getUserFields(self):
		return self.getModel().getUserFields()
	
	def getField(self,fieldId):
		return self.getModel().getModelField(fieldId)
	

	
	# ################ VIEW ENTRY CREATION
	
	def createDbEntry(self,parent,fieldsValuesDictionary=None):
		""" feeds the table with datas from the public form """
		
		# SOMETHING I'M TOO YOUNG TO UNDERSTAND : 
		# ACQUISITION DOESNT WORKS UNTIL THE END OF THE CREATION TRANSACTION
		
		tableName = self.getTableName()
		projectId = parent.getProject_db_id() 
		tablePkey = self.getTablePkey()
		userName = parent.portal_membership.getAuthenticatedMember().getId()
		
		creationRequest = FSZSQLMethod(self,self._FirstAddRequestFile)
		creationRequest.connection = parent.connection
		
		logSQL = creationRequest(projectId=projectId,tablePkey=tablePkey,tableName=tableName,userName=userName,fieldsValuesDictionary=fieldsValuesDictionary,src__=1)
		
		self.log = str(fieldsValuesDictionary) + logSQL
		
		creationRequest(projectId=projectId,tablePkey=tablePkey,tableName=tableName,userName=userName,fieldsValuesDictionary=fieldsValuesDictionary)
		
	def getLog(self):
		""" returns the request log """
		return self.log.replace("\n"," ").replace("\t"," ").replace("  "," ").replace(";",";\n")
		
	def getPublicFieldSQLAdress(self,publicFieldId):
		""" """
		return fieldId.replace('_in_','.')
		
	
	# #################### ENTRY UPDATE 
	
	def updateView(self,fieldsValuesDictionary):
		""" creates a new entry with fieldsDictionary """
		
		tableName = self.getTableName()
		projectId = self.getProject_db_id() 
		tablePkey = self.getTablePkey()
		userName = self.portal_membership.getAuthenticatedMember().getId()
		
		
		self._main_add = FSZSQLMethod(self,self._main_add_request_ZSQLFile)
		self._main_add.connection = self.connection
		
		logSQL = self._main_add(projectId=projectId,tablePkey=tablePkey,tableName=tableName,userName=userName,fieldsValuesDictionary=fieldsValuesDictionary,src__=1)
		
		self.log = str(fieldsValuesDictionary) + logSQL.replace("\r\n"," ")
		
		self._main_add(projectId=projectId,tablePkey=tablePkey,tableName=tableName,userName=userName,fieldsValuesDictionary=fieldsValuesDictionary)
	
		self.setViewUnupdate() # delete the cached values
	
	def setViewUnupdate(self):
		""" delete the cached values after view datas modification """
		self._reportDictionary = {}
		self._main_select = None
		
	# #################### REPORT REQUESTS
	
	def requestReport(self,fieldsList):
		""" gets a dictionary from fieldsList {id:(label,value|[values])} for report
		by requesting the database
				
		for example 
		RequestReview.requestReport(self,[description,delay]) ->
			{'description':('Project request description','A software to manage projects'),
			 'delay':(DateTime('15-09-2006'))}
			
		it may be more complex (redefine getReportDictionary or _report_request_ZSQLFile)

		
		"""
		
		# create report request
		if not hasattr(self,"_report_request") or self._deleteCache:
			self._report_request = FSZSQLMethod(self,self._report_request_ZSQLFile)
			self._report_request.connection = self.connection
		
		# log and execute report request
		logSQL = self._report_request(projectId= self.getProject_db_id(),
						tablePkey=self.getTablePkey(),
						tableName=self.getTableName(),
						fieldsList=fieldsList,
						src__=1)

		self.log = self.log + "\n" + str(fieldsList)+ "\n" + logSQL+"\n"
		
		reportRequestResults = self._report_request(projectId= self.getProject_db_id(),
						tablePkey=self.getTablePkey(),
						tableName=self.getTableName(),
						fieldsList=fieldsList)
		
		return self.getReportDictionary(fieldsList,reportRequestResults)
	
	_reportDictionary = {}
	def getReportDictionary(self,fieldsList,reportRequestResults):
		""" builds the report dictionary from the report request results
				this method may be low-level-user-defined
		
		THIS getReportDictionary METHOD :
			returns the latest value of each field for this project
		"""
		if self._reportDictionary: return self._reportDictionary
		
		if self._historicisedReport:
			# values are stored as a list
			for entry in reportRequestResults:
				for field in fieldsList:
					if not self._reportDictionary.has_key(field): 
						# first entry value
						self._reportDictionary[field] = (
							self.displayEntry(self.getField(field).get_value('title')),
							self.displayEntry([entry[field]])
							)
					
					else:
						# sequels
						self._reportDictionary[field][1].append([entry[field]])
						
		else:
			for entry in reportRequestResults:
				
				for field in fieldsList:
					self._reportDictionary[field] = (
						self.displayEntry(self.getField(field).get_value('title')),
						self.displayEntry(entry[field])
						)
					
				break
		
		return self._reportDictionary
		
# ########################################## CONCRETE VIEWS ####################################
		


class ProjectRequest(ProjectView):
		"""  provides a manager for the entry of contextual project in project requests table """
		_tableName = "project_requests"
		viewLabel = "project request"
		_table_pkey = "request_history_id__"
		_on_public_form = True
		
		view_description = "La définition du projet"
		
		pass
	
class ProjectDiary(ProjectView):
		"""  provides a manager for the entry of contextual project in project diary table """		
		_tableName = "project_diaries"
		viewLabel = "project diary"
		_table_pkey = "diary_entry_id__"
		
		view_description = "Le journal du projet"
		pass
	
class ProjectTrainings(ProjectView):
		"""  provides a manager for the entry of contextual project in project trainings table """		
		_tableName = "project_trainings"
		viewLabel = "project trainings"
		_table_pkey = "request_history_id__"
		
		pass
  
class ProjectUsers(ProjectView):
		"""  provides a manager for the entry of contextual project in project users table """		
		_tableName = "project_users"
		viewLabel = "project users"
		_on_public_form = "True"
		_table_pkey = "user_name__"
		
		_FirstAddRequestFile = "InraProjectsManager/SQLRequests/AddUserView.zsql"
		
		pass
	
class ProjectResults(ProjectView):
		"""  provides a manager for the entry of contextual project in project results table """		
		_tableName = "project_results"
		viewLabel = "project results"
		_table_pkey = "result_history_id__"
		
		view_description = "Les resultats du projet"
		
		pass

class ProjectRessources(ProjectView):
		""" provides a manager for the entry of contextual project in project ressources table """		
		_tableName = "project_ressources"
		viewLabel = "project ressources"
		_table_pkey = "request_history_id__"
		_historicisedReport = True
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