from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField,CMFObjectField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget, LabelWidget,LinesWidget
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod


from Products.InraProjectsManager.interfaces import IInraProject
from Products.InraProjectsManager import outils
from Products.InraProjectsManager.permissions import *
from Products.InraProjectsManager.config import *



def addInraProject(self,id,REQUEST=None,**kwargs):
	""" adds an Inra Projects Manager """
	object = InraProject(id,**kwargs)
	self._setObject(id, object)


factory_type_information = (
	{ 'id':'InraProject',
	 'meta_type':'InraProject',
	  'description':'A document that represents a project in a jouy platform',
	   'content_icon':'document_icon.gif',
	    'product':'InraProjectsManager',
	     'filter_content_types':True,
	      'allowed_content_types':(),
	      'global_allow':False,
	     'factory':'addInraProject',
	      'default_view':'edit',
	      'view_methods':('edit'),
	      'immediate_view':'edit',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'report_view',
		 	'permissions':(AddInraProjects,),
			},

	    		{'id':'projectResults',
	   		'name':'project Results',
	      		'action':'show_view?viewName=ProjectResults',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectResults" in object.getModelsList()'},
			
	    		{'id':'projectRequest',
	   		'name':'project Request',
	      		'action':'show_view?viewName=ProjectRequest',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectRequest" in object.getModelsList()'},
			
	    		{'id':'projectRessources',
	   		'name':'project Ressources',
	      		'action':'show_view?viewName=ProjectRessources',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectRessources" in object.getModelsList()'},
			
	    		{'id':'projectTrainings',
	   		'name':'project Trainings',
	      		'action':'show_view?viewName=ProjectTrainings',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectTrainings" in object.getModelsList()'},
			
	    		{'id':'projectUsers',
	   		'name':'project Users',
	      		'action':'show_view?viewName=ProjectUsers',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectUsers" in object.getModelsList()'},
	    		

		),

	   'aliases':(
	    	{
		'view':'report_view',
		'edit':'atct_edit',
		}),

	},
)

InraProjectSchema = Schema((
	
	IntegerField('project_id',
				
	       			read_permission=ModifyPortalContent,
		  		write_permission=ModifyPortalContent,
				mode="r",
	       			required=True,
		  		description="id of the project",
		  		widget=StringWidget(visible="{'edit':'invisible','view':'visible'}",),
	   ),

	StringField('person_in_charge',
	       			read_permission=ModifyPortalContent,
		  		write_permission=ModifyPortalContent,
	       			required=True,
		  		description="Login of the person in charge",
	      			mutator = "setPerson_in_charge",
		  		widget=StringWidget(label="Login of the person in charge"),
	   ),
	   
	StringField('customer_in_charge',
	       			read_permission=ModifyPortalContent,
		  		write_permission=ModifyPortalContent,
	       			required=True,
		  		description="Login of the person in charge",
	      			mutator = "setCustomer_in_charge",
		  		widget=StringWidget(label="Login of the person in charge"),
	   ),
	    

	StringField('live',
		read_permission=View,
		write_permission=ModifyPortalContent,
		required=True,
		default="live",
		vocabulary=DisplayList(LIVE_LEVELS),
		mutator="setLiveLevel",
		description="The email where to notify new requests",
		widget=SelectionWidget(label="Emails adresses where requests will be notified"),
		),
	
	StringField('confidentiality',
		write_permission=AddInraProjects,
		
		default_method="getDefault_confidentiality",
		mutator="setConfidentiality",
		read_permission=AddInraProjects,
		required=True,
		description="The confidentiality level",
		vocabulary=DisplayList(CONFIDENTIALITY_LEVELS),
		widget=SelectionWidget(
			label="The confidentiality level",
			),
		),
	))


class InraProject(ATFolder):
	""" Provides an object that manages a project """
	__implements__ = ATFolder.__implements__ + (IInraProject,)
	""" Provides an object that manages a project """
	
	archetype_name = "Inra Project"
	
	schema = ATFolder.schema + InraProjectSchema
	
	_deleteCache = True
	
	security = ClassSecurityInfo()
	
	def getProjectDbKey(self,):
		""" gets the identifier of that project in the database """
	
	def createViews(self,):
		""" creates the views of the project """
		pass
	
	def getView(self,viewNameStr):
		""" gets the view viewNameStr """
		return getattr(self,viewNameStr)
	
	def getViews(self):
		""" returns the dict of views """
		return self._views
	
	# ################ VIEWS CREATION
	
	def initProjectViews(self,viewFieldsValuesDictionary):
		""" creates the views of the project and feed them with public form values """
		
		for view in viewFieldsValuesDictionary:
			self.initProjectView(view,viewFieldsValuesDictionary[view])
		
	def initProjectView(self,viewClass,fieldsValuesDictionary):
		""" creates and ititializes the project view with public form values """
		newView = viewClass()
		self._setObject(viewClass.__name__,newView)
		newView.createDbEntry(fieldsValuesDictionary)
		
		
		
	# ###### mutators
	
	
	def setConfidentiality(self,confidentiality):
		self.confidentiality = confidentiality
		self._updateDbProjectValue('confidentiality__',confidentiality)
	
	
	def setPerson_in_charge(self,person_in_charge):
		self.person_in_charge = person_in_charge
		self._updateDbProjectValue('user_in_charge__',person_in_charge)
		
	def setCustomer_in_charge(self,customer_in_charge):
		self.customer_in_charge = customer_in_charge
		self._updateDbProjectValue('customer_in_charge__',customer_in_charge)
	
	def setLiveLevel(self,live):
		self.live = live
		self._updateDbProjectValue('life__',live)
	
	
	security.declareProtected("_updateDbProjectValue",ModifyPortalContent)
	def _updateDbProjectValue(self,field,value):
		if not hasattr(self,'_updateProjectValueRequest') or self._deleteCache:
			self._updateProjectValueRequest = FSZSQLMethod(self,UPDATE_PROJECT_VALUE_ZSQLFile)
			self._updateProjectValueRequest.connection = self.connection
		pass
		
		self._updateProjectValueRequest(project_id=self.project_id,fieldName=field,value=value)


	
	def getZSQLTypeOfValue(self,value):
		""" returns zsql type of value """
		if outils.same_type(value,1.1):
			return "float"
		elif outils.same_type(value,1):
			return "int"
		else:
			return "string"
	
	# ####### view related methods
	
	
	# ######## vocabularies
	
	def _report_fields_vocabulary(self):
		return DisplayList(())
		
		
registerType(InraProject)