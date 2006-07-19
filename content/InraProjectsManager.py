import psycopg2

from AccessControl import ClassSecurityInfo


from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField,CMFObjectField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget, LabelWidget

from Products.InraProjectsManager.interfaces import IInraProjectsManager
from Products.InraProjectsManager.permissions import AddInraProjectManager, AddInraProjects

from ProjectViewModelsManager import ProjectViewModelsManager

def addInraProjectsManager(self,id,REQUEST=None,**kwargs):
	""" adds an Inra Projects Manager """
	object = InraProjectsManager(id,**kwargs)
	self._setObject(id, object)

	
factory_type_information = (
	{ 'id':'InraProjectsManager',
	 'meta_type':'InraProjectsManager',
	  'description':'A container that manages projects and its views',
	   'title':'Inra Projects Manager',
	   'content_icon':'multiform.gif',
	    'product':'InraProjectsManager',
	     'filter_content_types':True,
	      'allowed_content_types':('InraProject','ProjectViewModelsManager'),
	     'factory':'addInraProjectsManager',
	      'default_view':'folder_listing',
	      'view_methods':('folder_listing','view_request_form','view_projects'),
	      'immediate_view':'view',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'(selected layout)',
		 	'permissions':(AddInraProjectManager,)},
			
	    		{'id':'edit_models',
	   		'name':'Edit models',
	      		'action':'edit_models',
		 	'permissions':(AddInraProjectManager,)},
			
			),

	   'aliases':(
	    	{'view':'(selected layout)',
	     	'edit':'atct_edit',
	        'properties':'base_metadata',
		'sharing':'folder_localrole_form',
		 }),

	},
)

InraProjectsManagerSchema = Schema((

	StringField('connection_info',
	       			read_permission=AddInraProjectManager,
		  		write_permission=AddInraProjectManager,
	       			required=True,
		  		description="The connection informations",
	      			mutator="majConnection",
		  		widget=StringWidget(label="The connection string"),
	   ),


	))

class InraProjectsManager(ATFolder):
	""" provides objects that manages the projects of one type in INRA """
	
	_connection = str() # a Z connecter to the projects database
	_connection_info = str() # the connection string to the database
	_publicRequestFieldsList = [] #
	
	__implements__ = ATFolder.__implements__ + (IInraProjectsManager,)
	
	archetype_name="Inra Projects Manager"
	
	schema = ATFolder.schema.copy() + InraProjectsManagerSchema
	
	security = ClassSecurityInfo()
	_at_rename_after_creation = True
	
	
		
	def getManagedViewsList(self):
		""" list of views on the projects managed by this projects manager """
		pass

	
	# ################## CONNECTION RELATED METHODS #################################
	
	security.declarePublic('getDBMSName')
	def getDBMSName(self):
		""" returns the name of the sgbd """
		return self._DBMSName

	
	security.declareProtected(AddInraProjectManager,'addConnection')
	def addConnection(self,connection_info,**kwargs):
		""" (psycopg) creates the connection, if not exists """
		try:
			self.manage_addProduct['ZPsycopgDA'].manage_addZPsycopgConnection("connection","connection",connection_info,check=True)
			self.connection_info = connection_info
			return True
		except psycopg2.OperationalError:
			return False
	
			
	security.declareProtected(AddInraProjectManager,'majConnection')
	def majConnection(self,connection_info,**kwargs):
		""" (all) changes connection informations 
		 creates a db connector if not exists """
		if not(hasattr(self,'connection')):
			self.addConnection(connection_info,**kwargs)
		else:
			self.setConnectionInfo(connection_info)
		pass
	
	security.declareProtected(AddInraProjectManager,'setConnectionInfo')
	def setConnectionInfo(self,connection_string):
		""" sets connection_string value (psycopg), returns False if connection string is bad """
		self.connection.manage_close_connection()
		old_connection_info = self.connection.connection_info
		
		self._DBStructure = {} # initialize db structure in 'cache'
		
		try:
			self.connection.connection_string = connection_string
			
			self.connection.manage_open_connection()
			self.connection_info = connection_string
			self.connection.manage_close_connection()
			return True
		
		except psycopg2.OperationalError:
			self.connection.connection_string = old_connection_info
			self.connection_info = old_connection_info
			return False
		
			
	# ############################## PROJECTS RELATED METHODS
	
	def getInraProjects(self,):
		""" the list of projects actually stored """
	
	def addInraProject(self,REQUEST):
		""" adds a project (from requestForm) """
	
		
	def executeRequestForm(self,):
		""" manages displaying, submission, validation, treatment of the form provided to public. always returns XHTML code. uses requestView model with publicRequestFieldsList """
	
	def setupRequestForm(self,):
		""" creates or updates the public request form """
		pass
	
	security.declareProtected("edit_models",AddInraProjectManager)
	def edit_models(self,REQUEST=None,**kwargs):
		""" creates the models manager if it doesn't exists. else, displays the edit form """
		models = self.getProjectViewModelsManager()
		REQUEST.response.redirect(models.absolute_url())
	
	security.declareProtected("getProjectViewModelsManager",AddInraProjectManager)
	def getProjectViewModelsManager(self):
		""" gets the models manager at self.model , and adds it if not exists"""	
		
		if not(hasattr(self,"models")):
			self.invokeFactory('ProjectViewModelsManager','models')
			obj = self['models']
			obj.setTitle("Models Manager")
			obj.reindexObject()
			
		return self.models

			
class InraRequestForm(object):
	""" The object that manages the public request form, its validation and its submission """
	pass
	
registerType(InraProjectsManager)