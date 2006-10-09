from AccessControl import ClassSecurityInfo


import psycopg2
import datetime

from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget
from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod

from Products.InraProjectsManager.interfaces import IProjectViewModelsManager
from Products.InraProjectsManager.permissions import AddInraProjectManager
from Products.InraProjectsManager.config import *

from ProjectViews import getProjectViewsList

def addProjectViewModelsManager(self,id,REQUEST=None,**kwargs):
	""" adds an Inra View Models Manager """
	object = ProjectViewModelsManager(id,**kwargs)
	self._setObject(id, object)

factory_type_information = (
	{ 'id':'ProjectViewModelsManager',
	 'meta_type':'ProjectViewModelsManager',
	  'description':'A container that manages projects views',
	   'content_icon':'multiform.gif',
	    'product':'InraProjectsManager',
	     'filter_content_types':True,
	      'allowed_content_types':('ProjectReport'),
	      'global_allow':False,
	     'factory':'addProjectViewModelsManager',
	      'default_view':'edit',
	      'view_methods':('edit'),
	      'immediate_view':'atct_edit',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'atct_edit',
		 	'permissions':(AddInraProjectManager,),
			},
			
	    		{'id':'projectResults',
	   		'name':'project Results',
	      		'action':'edit_model?modelName=ProjectResults',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectResults" in object.getModelsList()'},
			
	    		{'id':'projectRequest',
	   		'name':'project Request',
	      		'action':'edit_model?modelName=ProjectRequest',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectRequest" in object.getModelsList()'},
			
	    		{'id':'projectRessources',
	   		'name':'project Ressources',
	      		'action':'edit_model?modelName=ProjectRessources',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectRessources" in object.getModelsList()'},
			
	    		{'id':'projectTrainings',
	   		'name':'project Trainings',
	      		'action':'edit_model?modelName=ProjectTrainings',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectTrainings" in object.getModelsList()'},
			
	    		{'id':'projectUsers',
	   		'name':'project Users',
	      		'action':'edit_model?modelName=ProjectUsers',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectUsers" in object.getModelsList()'},
	    		
	    		{'id':'projectDiary',
	   		'name':'project diary',
	      		'action':'edit_model?modelName=ProjectDiary',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectDiary" in object.getModelsList()'},
	    		
		),

	   'aliases':(
	    	{
		'view':'atct_edit',
	     	'edit':'atct_edit',
		}),

	},
)


ProjectViewModelsManagerSchema = Schema((
	LinesField('modelsList',
			read_permission=View,
			write_permission=AddInraProjectManager,
	   		mutator="setModelsList",
			default=tuple(),
	   		vocabulary="_get_modelsList_vocabulary",
	      		description="List of views managed by PloneDbFormulator",
		 	widget = MultiSelectionWidget(
 	    			description="List of tables managed by PloneDbFormulator",
		 		label="Managed Views List",
			)
	   ),
	   ))

class ProjectViewModelsManager(OrderedBaseFolder):
	""" contains and manages the data models of the project type managed by this inraProjectsManager
	contains and manages the reports models
	"""
	
	__implements__ = OrderedBaseFolder.__implements__ + (IProjectViewModelsManager,)
	
	archetype_name="Project View Models Manager"
	schema         = OrderedBaseFolder.schema.copy() + ProjectViewModelsManagerSchema
	
	security = ClassSecurityInfo()
	_at_rename_after_creation = False
	
	# #######################################################################################
	# #				MODELS MANAGEMENT 					#
	# #######################################################################################
	
	def setModelsList(self,modelsList):
		self.modelsList = modelsList
		self.getPublicForm().setUnupdated()

	
	def getViewDbTables(self,):
		""" returns the list of the tables in the database, view Names and View Classes that corresponds to a view managed by this product """
		
		projectViewsList = getProjectViewsList()
		dbTablesList = self.getDbTablesList()
		
		return [(projectView.viewLabel,projectView._tableName,projectView) for projectView in projectViewsList if projectView._tableName in dbTablesList]
	
	def getViewOfTable(self,tableName):
		""" returns view of table """
		projectViewsList = getProjectViewsList()
		for view in projectViewsList:
			if view._tableName == tableName:
				return view
		
	def _getProjectView(self,viewName):
		""" returns the view class named viewName """
		viewDbTables = self.getViewDbTables()
		for projectView in viewDbTables:
			if projectView[2].__name__ == viewName:
				return projectView[2]
		#raise "Project View is not managed"
	
			
	
	def getDbTablesList(self,):
		""" returns the list of database tables """
		
		# saves the request : request caches the results
		if not(hasattr(self,"_tablesListRequest")):
			self._tablesListRequest = FSZSQLMethod(self,DB_TABLES_LIST_ZSQLFile)
			self._tablesListRequest.connection = self.connection
			pass
			
		request = self._tablesListRequest
		#request.connection.manage_open_connection()
		tablesList = [result['tablename'] for result in request() \
			if not(result['tablename'].startswith("pg_") or result['tablename'].startswith("sql_"))]
		#request.connection.manage_close_connection()
		
		return tablesList
	

		

	security.declareProtected("edit_model",AddInraProjectManager)
	def edit_model(self,modelName,REQUEST=None):
		""" displays the model manager """
		REQUEST.response.redirect(self.getModel(modelName)[0].absolute_url())
		
	
	# ###################### MODELS GETTERS
		
	security.declareProtected("getModelsList",View)
	def getModelsList(self,):
		""" returns a dict str modelName : obj modelObject, modelObject = False if modelhas not been setup """
		
		modelsList = {}
		
		if self.modelsList:
			for managedModel in self.modelsList:
				createdModels = self.models.objectIds()
				if managedModel in createdModels:
					model = getattr(self.models,managedModel)
					modelsList[managedModel] = [False,model][int(hasattr(model,"form"))]
					
				else:
					modelsList[managedModel] = False
					pass
				
		return modelsList
	
	security.declareProtected("getSetupModels",View)
	def getSetupModels(self):
		""" returns the list of models that have been setup """
		modelsList = self.getModelsList()
		# models list = dictionary {modelName: modelObject|False}
		return	[modelsList[modelName] for modelName in modelsList if modelsList[modelName]]
		
	security.declareProtected("getModel",View)
	def getModel(self,modelName):
		""" returns the (ProjectViewModel object, isSetup boolean) named modelName
		 creates the model it if necessary """
		modelsList = self.getModelsList()
		if not modelName in modelsList:
			raise AttributeError, modelName+" is not a managed view"
		
		if not modelName in self.models.objectIds():
			self.models._createModel(modelName)
		return getattr(self,modelName), modelsList[modelName]
	
	
	
	security.declareProtected("_setModel",AddInraProjectManager)
	def _createModel(self,modelName):
		getToolByName(self,'portal_types').constructContent('ProjectViewModel',self,modelName)
		obj = self[modelName]
		obj.setTitle(self._getProjectView(modelName).viewLabel+" model")
		obj.reindexObject()

	

	security.declareProtected("_get_modelsList_vocabulary",View)
	def _get_modelsList_vocabulary(self):
		viewsList = self.getViewDbTables()
		
		vocabulary = tuple()
		
		for view in viewsList:
			viewLabel = view[0]
			viewName = view[2].__name__
			vocabulary += ((viewName,viewLabel),)
				
		return DisplayList(vocabulary)
		
	
	# #######################################################################################
	# #				REPORT MANAGEMENT 					#
	# #######################################################################################
	
		
	_reportList = []
	def getReportList(self,):
		""" get list of reports -> [obj ProjectReport:projectReport]"""
		if not self._reportList:
			for object in self.objectItems():

				if object[1].meta_type == "ProjectReport":
					self._reportList.append(object[1])

		return self._reportList	

	def getReport(self,reportName):
		""" get report named reportname -> obj ProjectReport """
		for report in self.getReportList():
			if report.getId() == reportName:
				return report
		return None

	def setReportList(self,reportList):
		""" set reports list as -> [str:reportName]"""
		self._reportList = reportList

	_defaultReport = None
	def setDefaultReport(self,reportName):
		""" the report reportName is displayed at View action """
		self._defaultReport = self.getReport(reportName)
		for report in self.getReportList():
			if not report.getId() == reportName:
				report.unsetDefault()


	def getDefaultReport(self,):
		""" gets the default report """	
		if not self._defaultReport:
			if not self.getReportList():
				return None
			self._defaultReport = self._reportList[0]
		return self._defaultReport





registerType(ProjectViewModelsManager)