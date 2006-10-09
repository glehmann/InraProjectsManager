import psycopg2
from DateTime import DateTime

from AccessControl import ClassSecurityInfo


from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField,CMFObjectField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget, LabelWidget,LinesWidget
from Products.CMFCore.utils import getToolByName

from Products.InraProjectsManager.interfaces import IInraProjectsManager
from Products.InraProjectsManager.permissions import AddInraProjectManager, AddInraProjects

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod



from ProjectViewModelsManager import ProjectViewModelsManager
from Products.InraProjectsManager import outils
from Products.InraProjectsManager.permissions import *
from Products.InraProjectsManager.config import *



class StringDate:
	def __init__(self,date):
		self.year=date.year
		self.day=date.day
		self.month=date.month
		
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
	      'allowed_content_types':('InraProject'),
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
			
			{'id':'formulaire',
	   		'name':'formulaire',
	      		'action':'publicForm',
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
	LinesField('emails',
		read_permission=View,
		write_permission=AddInraProjectManager,
		required=True,
		description="The email where to notify new requests",
		widget=LinesWidget(label="Emails adresses where requests will be notified"),
		),
	
	StringField('default_confidentiality',
		write_permission=AddInraProjectManager,
		vocabulary=DisplayList(CONFIDENTIALITY_LEVELS),
		read_permission=View,
		required=True,
		description="The default confidentiality level",
		mutator="setDefault_confidentiality",
		widget=SelectionWidget(
			label="The default confidentiality level",
			),
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
	
	_deleteCache = True
	
	def getProjectsManager(self):
		return self
	
	# ################## CONNECTION RELATED METHODS #################################
	
	
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
	
	# ######### PROJECTS MANAGEMENT
	
	def getInraProjects(self,):
		""" the list of projects actually stored """
	
	# ################# MODELS MANAGER RELATED METHODS
	
	security.declareProtected("edit_models",AddInraProjectManager)
	def edit_models(self,REQUEST=None,**kwargs):
		""" creates the models manager if it doesn't exists. else, displays the edit form """
		#return "toto"
		models = self.getProjectViewModelsManager()
		return REQUEST.response.redirect(models.absolute_url())
	
	security.declareProtected("getProjectViewModelsManager",AddInraProjectManager)
	def getProjectViewModelsManager(self):
		""" gets the models manager at self.model , and adds it if not exists"""	
		
		if not(hasattr(self,"models")):
			getToolByName(self,"portal_types").constructContent('ProjectViewModelsManager',self,'models')
			obj = self['models']
			obj.setTitle("Configuration Manager")
			obj.reindexObject()
			
		return self.models
	
	security.declareProtected("getModelsList",View)
	def getModelsList(self,):
		""" returns a dict str modelName : obj modelObject, modelObject = False if modelhas not been setup """
		return self.models.getModelsList()
	
	# ############## REPORTS MANAGEMENT RELATED METHODS
	
	
	
	# ############## PUBLIC FORM RELATED METHODS
	
	def getPublicForm(self):
		""" gets the public form manager at self.publicForm, creates if not exists """
		
		if not "publicForm" in self.objectIds():
			getToolByName(self,"portal_types").constructContent('PublicProjectForm',self,'publicForm')
			obj = self['publicForm']
			obj.setTitle(self.Title()+" Form")
			obj.reindexObject()
		
		return self.publicForm
	
	def labelFromId(self,label):
		""" """
		return outils.labelFromId(label)
	
	# ########################## PROJECT CREATION
	
	def realize_publicForm_submission(self,viewFieldsValuesDictionary):
		""" executes the treatment of submission form by the creation of a new project """
		
		
		
		person_in_charge = self.project_affectation_script()
		
		
		
		customer_in_charge = getToolByName(self,'portal_membership').getAuthenticatedMember()
		
		#try:
		if 1:
			projectId = self._getCurrentProjectId()
			self.createInraProject(projectId,person_in_charge,customer_in_charge,viewFieldsValuesDictionary)
		
		'''	
		except:
			
			self.connection.manage_close_connection()
			self.connection.manage_open_connection()
			projectId = self._getNextProjectId()
			self.createInraProject(projectId,person_in_charge,customer_in_charge,viewFieldsValuesDictionary)
		'''
		#newProject._sendProjectCreationNotification()
		
		self.publicForm_post_script()
		newProject = getattr(self,"project_"+str(projectId))
		self.REQUEST.response.redirect(newProject.absolute_url())
		
		
	def createInraProject(self,projectId,person_in_charge,customer_in_charge,viewFieldsValuesDictionary):
		""" creates the inra project with id projectId managed by person_in_charge, 
		with the publicForm datas stored in viewFieldsValuesDictionary """
		
		project_PloneId = 'project_'+str(projectId)
		
		getToolByName(self,"portal_types").constructContent('InraProject',self,project_PloneId)
		newProject = self[project_PloneId]
		
		title = "Projet "+str(projectId)+" : "+customer_in_charge.name
			
		newProject.setTitle(title)
		newProject.project_id = projectId
		newProject.confidentiality = self.getDefault_confidentiality() # DON'T USE MUTATORS AT THIS MOMENT (mutator executes sql
		newProject.person_in_charge = person_in_charge.getId()
		newProject.customer_in_charge = customer_in_charge.getId()
		
		self.addInraProjectDbEntry(newProject)
		
		newProject.initProjectViews(viewFieldsValuesDictionary)
		
		newProject.reindexObject()
		
		return newProject
	
	security.declareProtected(AddInraProjects,"_getNextProjectId")
	def _getNextProjectId(self):
		if not(hasattr(self,"_getNextProjectIdRequest")) or self._deleteCache:
			self._getNextProjectIdRequest = FSZSQLMethod(self,RESTART_PROJECT_ID_ZSQLFile)
			self._getNextProjectIdRequest.connection = self.connection
		
		
		return self._getNextProjectIdRequest()[0][0]
		
	
	
	security.declareProtected(AddInraProjects,"_getCurrentProjectId")
	def _getCurrentProjectId(self):
		
		if not(hasattr(self,"_getCurrentProjectIdRequest")) or self._deleteCache:
			self._getCurrentProjectIdRequest = FSZSQLMethod(self,NEXT_PROJECT_ID_ZSQLFile)
			self._getCurrentProjectIdRequest.connection = self.connection
		
		
		return self._getCurrentProjectIdRequest()[0][0]
		
		
	def _sendProjectCreationNotification(self,newInraProject,REQUEST):
		""" sends a mail to announce the creation of a new project """
	
	def addInraProjectDbEntry(self,newProject):
		""" adds the entry of a new project in the database from the public form request datas """
		
		if not(hasattr(self,"_addInraProjectRequest")) or self._deleteCache:
			self._addInraProjectRequest = FSZSQLMethod(self,ADD_INRA_PROJECT_ZSQLFile)
			self._addInraProjectRequest.connection = self.connection
	
		self._addInraProjectRequest(
				user_in_charge=newProject.person_in_charge,
				customer_in_charge=newProject.customer_in_charge,
				confidentiality=self.getDefault_confidentiality()
			)
	
	
	# OUTILS
	
	
	security.declarePublic("fromStringToDate")
	def fromStringToDate(self,strdate):
		""" transforme une string 2006-12-21 en objet zope datetime """
		try:
		#if 1:
			strdate=str(strdate)
			if strdate=="" or strdate=="None":
				return None
			
			arraydate=strdate.split("-")
			if len(arraydate)==3 and int(arraydate[0])>1000 and int(arraydate[1])<=12:
				date = DateTime(int(arraydate[0]),int(arraydate[1]),int(arraydate[2]))
				return date
		
			else:
				raise ValueError
		#else:
		except:
				raise ValueError, "this string "+str(strdate)+" does not seems not to be a date (jj-mm-yyyy)"
			
	
registerType(InraProjectsManager)