from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField,CMFObjectField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget, LabelWidget,LinesWidget
from Products.CMFCore.utils import getToolByName

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
	      'default_view':'select_view',
	      'view_methods':('select_view'),
	      'immediate_view':'view',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'select_view',
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
		'view':'select_view',
		'edit':'atct_edit',
		}),

	},
)

InraProjectSchema = Schema((

	StringField('person_in_charge',
	       			read_permission=AddInraProjectManager,
		  		write_permission=AddInraProjectManager,
	       			required=True,
		  		description="Login of the person in charge",
	      			mutator = "setPerson_in_charge",
		  		widget=StringWidget(label="Login of the person in charge"),
	   ),
	StringField('live',
		read_permission=View,
		write_permission=AddInraProjectManager,
		required=True,
		default="live",
		vocabulary=DisplayList(LIVE_LEVELS),
		mutator="setLiveLevel",
		description="The email where to notify new requests",
		widget=SelectionWidget(label="Emails adresses where requests will be notified"),
		),
	
	StringField('confidentiality',
		write_permission=AddInraProjectManager,
		vocabulary=DisplayList(CONFIDENTIALITY_LEVELS),
		default="python:object.default_confidentiality",
		read_permission=AddInraProjects,
		required=True,
		description="The confidentiality level",
		
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