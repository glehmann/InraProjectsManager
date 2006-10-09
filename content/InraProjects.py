from AccessControl import ClassSecurityInfo
import psycopg2

from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField,CMFObjectField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget, LabelWidget,LinesWidget
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod

from Products.Formulator.Errors import FormValidationError

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
	      'default_view':'atct_edit',
	      'view_methods':('view_default_report','atct_edit'),
	      'immediate_view':'atct_edit',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'view_default_report',
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
	    		
	    		{'id':'projectDiary',
	   		'name':'project Diary',
	      		'action':'show_view?viewName=ProjectDiary',
		 	'permissions':(AddInraProjects,),
			'condition':'python:"ProjectDiary" in object.getModelsList()'},
	    		

		),

	   'aliases':(
	    	{
		'view':'view_default_report',
		'edit':'atct_edit',
		'sharing':'folder_localrole_form',
		'properties':'base_metadata',
		}),

	},
)

InraProjectSchema = Schema((
	
	IntegerField('project_id',
				
	       			read_permission=View,
		  		write_permission=ManageInraProject,
				mode="r",
	       			required=True,
		  		description="id of the project",
		  		widget=StringWidget(visible="{'edit':'invisible','view':'visible'}",),
	   ),

	StringField('person_in_charge',
	       			read_permission=View,
		  		write_permission=ManageInraProject,
	       			required=True,
		  		description="Login of the person in charge",
	      			mutator = "setPerson_in_charge",
		  		widget=StringWidget(label="Login of the person in charge"),
	   ),
	   
	StringField('customer_in_charge',
	       			read_permission=View,
		  		write_permission=ManageInraProject,
	       			required=True,
		  		description="Login of the customer in charge",
	      			mutator = "setCustomer_in_charge",
		  		widget=StringWidget(label="Login of the customer in charge"),
	   ),
	    

	StringField('live',
		read_permission=View,
		write_permission=ManageInraProject,
		required=True,
		default="live",
		vocabulary=DisplayList(LIVE_LEVELS),
		mutator="setLiveLevel",
		description="Life state of the project document",
		widget=SelectionWidget(label="Life state of the project document"),
		),
	
	StringField('confidentiality',
		write_permission=ManageInraProject,
		default_method="getDefault_confidentiality",
		mutator="setConfidentiality",
		read_permission=View,
		required=True,
		description="The confidentiality level",
		vocabulary=DisplayList(CONFIDENTIALITY_LEVELS),
		widget=SelectionWidget(
			label="The confidentiality level",
			),
		),
	))


class InraProject(OrderedBaseFolder):
	""" Provides an object that manages a project """
	__implements__ = OrderedBaseFolder.__implements__ + (IInraProject,)
	""" Provides an object that manages a project """
	
	archetype_name = "Inra Project"
	
	schema = OrderedBaseFolder.schema + InraProjectSchema
	
	_deleteCache = True
	
	security = ClassSecurityInfo()
	
	def getProject_db_id(self,):
		""" gets the identifier of that project in the database """
		return self.project_id
	
		
	def createViews(self,):
		""" creates the views of the project """
		pass

	# #######################################################
	# ######################## VIEWS ########################
	# #######################################################
	
	def getView(self,viewNameStr):
		""" gets the view viewNameStr """
		return getattr(self,viewNameStr)
	
	def getViews(self):
		""" returns the dict of views """
		return self._views
	
		
	# ################ VIEWS CREATION
	
	def initProjectViews(self,viewFieldsValuesDictionary):
		""" creates the views of the project and feed them with public form values """
		
		# for each model that have been setup :
		for setupModel in self.models.getSetupModels():
			
			# gets the view class corresponding to this model
			viewClass = setupModel.getViewClass()
			
			if viewClass in viewFieldsValuesDictionary: # if there are publicFields completed for this view
				self.initProjectView(viewClass,viewFieldsValuesDictionary[viewClass])
			else:
				self.initProjectView(viewClass)
	
	def initProjectView(self,viewClass,fieldsValuesDictionary={}):
		""" creates and ititializes the project view with public form values """
	
		viewName = str(viewClass.__name__)
		newView = viewClass(viewName,viewName)
		self._setObject(viewName,newView)
	
		newView.createDbEntry(parent=self,fieldsValuesDictionary=fieldsValuesDictionary)
	
	
	# ################# VIEWS DISPLAYING
	
	def show_view(self,viewName,REQUEST=None,error_value=None):
		""" displays the view viewName """
		
		view = self.getView(viewName)
		REQUEST.set("shownView",view)
		# on est obligés de faire tout ça dans le projet, et pas dans la vue, (d'où conception bizarre) 
		# sinon plone ne reconnait pas le projet comme l'objet courant -> probleme d'interface
		
		try:
			request = view.getMainSelectRequest()
		except:
			self.connection.manage_close_connection()
			self.connection.manage_open_connection()
			request = view.getMainSelectRequest()
		
		results = request(tablePkey=view.getTablePkey(),
				projectId=self.getProject_db_id(),
				tableName=view.getTableName())
		
		_view_main_template_layer = getattr(self,view.getView_main_template_name())

		return _view_main_template_layer(REQUEST=REQUEST,error_value=error_value,results=results,shownView=view)
		
		
	def modelFields(self):
		""" fields of the model [instance] """
		return self.REQUEST.shownView.getModel().getFields()
	
	
	def displayEntry(self,entryValue):
		""" formats and displays the content of an entry value """
		if entryValue == None:
			return unicode()
		else:
			try:
				entryValue = str(entryValue).decode("utf-8")
			except AttributeError:
				pass
		return entryValue
			


	# ################### VIEWS UPDATING

	def submit_updateView_form(self,REQUEST=None):
		""" treatment of view form submission : validation and sending updated datas to the view """
		viewName = REQUEST['viewName']
		updatedView = self.getView(viewName) # view to be updated
		model = updatedView.getModel()
		
		try:
			fieldsDictionary = {}
			submittedForm = model.form.validate_all_to_request(REQUEST)
			
			for fieldName in submittedForm:
				if submittedForm[fieldName]:
					fieldsDictionary[fieldName] = submittedForm[fieldName]
					
			fieldsDictionary["comment__"] = REQUEST["comment__"]
			
			updatedView.updateView(fieldsDictionary)
			
		except FormValidationError, error_value:
			return self.show_view(viewName,REQUEST=REQUEST,error_value=error_value)
			
		return self.show_view(viewName,REQUEST=REQUEST)
	
	def currentOrUserFieldValue(self,field,entry,REQUEST,error_value):
		""" very dirty : gets the value of a html field in a view : if not set by a user, the entry in the db """
		if not error_value:
			return entry[field.getId()]
		else:
			return field.render_from_request(REQUEST)
		
	
	# ### template methods
	
	def user_fields(self):
		""" user-defined fields of the model """
		return self.REQUEST.shownView.getUserFields()
	
	'''
	def field_label(self,fieldId):
		""" """
		return self.REQUEST.shownView.getField(fieldId).get_value('title')
	'''
	'''
	def getField(self,fieldId):
		""" """
		return self.REQUEST.shownView.getModel().form.get_field(fieldId)
	'''

	def getFormMessage(self):
		return "Add"

	
	
	# ######## vocabularies
	
	'''
	def _report_fields_vocabulary(self):
		return DisplayList(())
	'''
		
	# #####################################################
	# ##################### REPORTS #######################
	# #####################################################
	
	security.declareProtected(View,"view_default_report")
	def view_default_report(self,REQUEST=None):
		""" view the default report. default View method """
		report = self.models.getDefaultReport()
		return self.view_report(report.getId(),REQUEST)
	
	
	def view_report(self,reportName,REQUEST=None):
		""" displays the report reportName """
		
		report = self.getReport(reportName)
		self.REQUEST.set("shownReport",report)
		
		# on est obligés de faire tout ça dans le projet, et pas dans la vue, (d'où conception bizarre) 
		# sinon plone ne reconnait pas le projet comme l'objet courant,
		# ce qui provoque de gros problemes d'interface graphique
		this_project=self
		reportDictionary = report.buildReportDictionary(this_project)
		reportTemplate = getattr(self,report.getTemplateName())
		
		return self.project_report_main(reportTemplate=reportTemplate,
						reportDictionary=reportDictionary)
		
	
	def getReport(self,reportName):
		""" gets the report named reportName in the Configuration Manager """
		return getattr(self.models,reportName)
		
		
	# #######################################################
	# ################# PROJECT PROPERTIES ##################
	# #######################################################
	
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
	
	# ##### default
	
	def getDefault_confidentiality(self):
		return self.default_confidentiality
	
	# outils
		
	def getZSQLTypeOfValue(self,value):
		""" returns zsql type of value """
		if outils.same_type(value,1.1):
			return "float"
		elif outils.same_type(value,1):
			return "int"
		elif outils.same_type(value,'') or outils.same_type(value,u''):
			return "string"
		
	
registerType(InraProject)