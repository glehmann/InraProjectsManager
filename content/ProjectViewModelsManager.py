from AccessControl import ClassSecurityInfo

import psycopg2

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

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
	      'allowed_content_types':(),
	      'global_allow':False,
	     'factory':'addProjectViewModelsManager',
	      'default_view':'folder_listing',
	      'view_methods':('folder_listing'),
	      'immediate_view':'view',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'(selected layout)',
		 	'permissions':(AddInraProjectManager,),
			},
			
	    		{'id':'projectResults',
	   		'name':'projectResults',
	      		'action':'projectResults',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectResults" in object.getModelsList()'},
			
	    		{'id':'projectRequest',
	   		'name':'projectRequest',
	      		'action':'projectRequest',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectRequest" in object.getModelsList()'},
			
	    		{'id':'projectRessources',
	   		'name':'projectRessources',
	      		'action':'projectRessources',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectRessources" in object.getModelsList()'},
			
	    		{'id':'projectTrainings',
	   		'name':'projectTrainings',
	      		'action':'projectTrainings',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectTrainings" in object.getModelsList()'},
			
	    		{'id':'projectUsers',
	   		'name':'projectUsers',
	      		'action':'projectUsers',
		 	'permissions':(AddInraProjectManager,),
			'condition':'python:"ProjectUsers" in object.getModelsList()'},
		),

	   'aliases':(
	    	{'view':'(selected layout)',
	     	'edit':'atct_edit',
		'sharing':'folder_localrole_form',
		 }),

	},
)

#  

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

class ProjectViewModelsManager(ATFolder):
	""" contains and manages the data models of the project type managed by this inraProjectsManager 
	"""
	
	__implements__ = ATFolder.__implements__ + (IProjectViewModelsManager,)
	
	archetype_name="Project View Models Manager"
	schema         = ATFolder.schema.copy() + ProjectViewModelsManagerSchema
	
	security = ClassSecurityInfo()
	_at_rename_after_creation = False
	
	
	
	security.declareProtected("getModelsList",AddInraProjectManager)
	def getModelsList(self,):
		""" returns a list of tuples
		(model,isSetup), containing each model listed in managedViewsList, with isSetup = True if the model has been setup, and else isSetup = False """
	
	security.declareProtected("getViewDbTables",AddInraProjectManager)
	def getViewDbTables(self,):
		""" returns the list of the tables in the database, view Names and View Classes that corresponds to a view managed by this product """
		
		projectViewsList = getProjectViewsList()
		dbTablesList = self.getDbTablesList()
		
		return [(projectView.viewLabel,projectView._tableName,projectView) for projectView in projectViewsList if projectView._tableName in dbTablesList]
		
		
	security.declareProtected("getDbTablesList",AddInraProjectManager)
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
	
			
	
	def getModelsList
	
	def _get_modelsList_vocabulary(self):
		viewsList = self.getViewDbTables()
		
		vocabulary = tuple()
		
		try:
			for view in viewsList:
				viewLabel = view[0]
				viewName = view[2].__name__
				vocabulary += ((viewName,viewLabel),)
				
		except psycopg2.ProgrammingError:
			pass

		return DisplayList(vocabulary)
		
	
	# TESTS
	def test_getProjectViewsList(self):
		""" tests """
		return getProjectViewsList()
	
registerType(ProjectViewModelsManager)