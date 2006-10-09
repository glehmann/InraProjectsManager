from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, ManagePortal

from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder
from Products.Archetypes.public import BaseFolder, BaseSchema, Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, LinesField, ReferenceField
from Products.Archetypes.public import MultiSelectionWidget, BooleanWidget, SelectionWidget
from Products.Archetypes.public import ReferenceWidget

from Products.PageTemplates import PageTemplateFile

from Products.Formulator.Form import ZMIForm
from Products.Formulator import Form
from Products.Formulator.Errors import ValidationError, FormValidationError

from Globals import DTMLFile
from OFS.DTMLMethod import DTMLMethod
from Products.PythonScripts.PythonScript import PythonScript

import psycopg2

from Products.InraProjectsManager.interfaces import IPublicProjectForm
from Products.InraProjectsManager.config  import *
from Products.InraProjectsManager.permissions import *
from Products.InraProjectsManager import outils

#from Products.PloneDbFormulator.PloneDbFormsManager import PloneDbFormsManager


def addPublicProjectForm(self,id,REQUEST=None,**kwargs):
	""" adds a form manager in the self container """
	
	""" for the moment, can only create it in a PloneDbFormsManager """
	object = PublicProjectForm(id,**kwargs)
	self._setObject(id, object)
	form = ZMIForm("form", "form", unicode_mode=True)
	object._setObject("form",form)

factory_type_information = (
	{ 'id':'PublicProjectForm',
	'meta_type':'PublicProjectForm',
	'description':'An interaction form to the database',
	'title':'PublicProjectForm',
	'content_icon':'formmanager.gif',
	'product':'InraProjectsManager',
	'factory':'addPublicProjectForm',
	'default_view':'view_form',
	'immediate_view':'edit',
	'filter_content_types':True,
	'allowed_content_types':(),
	'global_allow':False,
	'actions':(
		{'id':'view',
			'name':'View the public form',
			'action':'view_form',
			'visible':1,
			'permissions':(View,)},
		{'id':'edit',
			'name':'Edit Form Properties',
			'visible':1,
			'action':'edit',
			'permissions':(AddInraProjectManager,)},
			

		{'id':'customizepre_script_project',
			'name':'customize pre script',
			'action':'customizepre_script_project',
			'visible':1,
			'category':'object_buttons',
			'permissions':(AddInraProjectManager,)},
			
		{'id':'customizepost_script_project',
			'name':'customize post script',
			'action':'customizepost_script_project',
			'visible':1,
			'category':'object_buttons',
			'permissions':(AddInraProjectManager,)},
			
		{'id':'customizepublicForm_body',
			'name':'customize public form',
			'action':'customizepublicForm_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(AddInraProjectManager,)},
					
		{'id':'customize_form',
			'name':'customize_form',
			'action':'customize_form',
			'visible':0,
			'permissions':(AddInraProjectManager,)},
			
		{'id':'setCustomized',
			'name':'setCustomized',
			'action':'setCustomized',
			'visible':0,
			'category':'object_buttons',
			'permissions':(AddInraProjectManager,)},
		
		{'id':'setDefault',
			'name':'set default',
			'action':'setDefault',
			'visible':0,
			'permissions':(AddInraProjectManager,)},

	    	{'id':'edit_models',
	   		'name':'Edit models',
	      		'action':'edit_models',
		 	'permissions':(AddInraProjectManager,)},
			
					
		),
			
		
	'aliases':({
		'view' : 'view_form',
		'edit'	: 'base_edit',
		'sharing' : 'sharing',
		'properties':'base_metadata'
		}),

	},
)	


PublicProjectFormSchema  = Schema(tuple())


class PublicProjectForm(OrderedBaseFolder):
	""" manages an interaction form with a database. search form by default """
	
	__implements__ = OrderedBaseFolder.__implements__ + (IPublicProjectForm,) 
	schema         = OrderedBaseFolder.schema.copy()+ PublicProjectFormSchema
	_at_rename_after_creation = True
	
	
	archetype_name = "Public Project Form"
	
	security = ClassSecurityInfo()
	
	_isUpdate=False
	
	view_form_zptfile = PageTemplateFile.PageTemplateFile('../templates/view_form.zpt',globals())
	
	def getFormType(self):
		return "publicForm"
	
	# ################# FORM UPDATING
	
	security.declareProtected(View,'isUpdate')
	def isUpdate(self):
		""" returns true if project form is up to date """
		return self._isUpdate
	
	security.declareProtected(View,'updateForm')
	def updateForm(self):
		""" creates and updates the public form, using hard-coded fields and dynamical user fields of models """
				
		modelFieldsList = self.getPublicFieldsList()
		modelFieldsIds = [field.getId() for field in modelFieldsList]
		
		form = self.publicForm.form
		
		
		# deletes fields in publicForm but not those of model
		form.manage_delObjects([publicFieldId for publicFieldId in form.get_field_ids() \
					if not(publicFieldId in modelFieldsIds)])
		test = ""
		for modelField in modelFieldsList: # updates all the public fields
			test += modelField.getId()
			self.updateField(modelField)
		
		self.getFieldsGroups() # recalculate fields groups
			
		#return test
		self._isUpdate = True
		
		return self.form
		
	security.declareProtected(AddInraProjectManager,'setUnupdated')
	def setUnupdated(self):
		""" sets that the form has to be updated to be conform to new configurations """
		self._isUpdate = False
	
	security.declareProtected(View,'updateField')
	def updateField(self,modelField): # LE METTRE EN PRIVATE PAR LA SUITE
		""" copy model fields into the publicForm. old ones are just updated except if their type has changed """
		
		publicForm = self.publicForm.form
		
		publicFieldId = self.getPublicFormId(modelField)
		
		if not(publicFieldId in publicForm.objectIds()):
			# adds lacking fields in form
			publicForm.manage_clone(modelField,publicFieldId)
	
		# if exists, initialize values with model ones
		
		getattr(publicForm,publicFieldId).initialize_values(modelField.values)
		return modelField,modelField.values,getattr(publicForm,publicFieldId)
		pass
			
	def getPublicFormId(self,field):
		return field.getTableName() + "_in_" + field.getId()
			
	security.declareProtected(View,'getPublicFieldsList')
	def getPublicFieldsList(self):
		""" returns the list of public form fields as a dictionary object field : str table_name """
		modelFieldsList = {}
		for setupModel in self.models.getSetupModels(): # for each model that have been set up
			table_name = setupModel.getTableName()
			fieldsOnPublicForm_model = setupModel.getFieldsOnPublicForm()
			if fieldsOnPublicForm_model:
				for modelField in fieldsOnPublicForm_model:
					modelFieldsList[modelField] = table_name
		
		return modelFieldsList
	
				

				
	# ################# FORM DISPLAYING AND EXECUTION ######
	
	def view_form(self,REQUEST=None):
		""" updates and launch form displaying """
		if not(self.isUpdate()):
			self.updateForm()
		
		return self.view_form_zptfile(REQUEST=self.REQUEST)
	
	log = ""
	
	def getLog(self):
		return self.log
	
	def execute_publicForm(self,REQUEST=None):
		""" displays, validates and controls the public form submission """
				
		if REQUEST:
			
			try:
				self.form.validate_all_to_request(REQUEST)
			
			except FormValidationError, error_value:
					
				return self.form.header() +\
					self.publicForm_body(self,error_value=error_value) +\
					self.form.footer()
		
		
		 # if form has been submitted and is not empty
			if self.emptyForm(REQUEST):
			
				return self.form.header() +\
					self.publicForm_body(self) +\
					self.form.footer()

			else:
				viewFieldsValuesDictionary = self.getViewFieldsValuesDictionaryFromRequest(REQUEST)
				self.log= str(self.log) + str(REQUEST.form)+"\n"
				self.realize_publicForm_submission(viewFieldsValuesDictionary)
				
	def emptyForm(self,REQUEST=None,**kwargs):

		""" returns true if the form hasn't yet been completed at all, or false """
		REQUEST = self.REQUEST
		if not REQUEST.form.has_key("formulator_submission"): return True
		if not(REQUEST.form["formulator_submission"]):return True
		for field in self.form.get_fields():
			 if REQUEST.get(field.getId()):
				 return False
		return True

	#  REQUEST DATA ANALYSE
	
	def getViewFieldsValuesDictionaryFromRequest(self,REQUEST):
		""" returns a dictionary :
			
			{str viewClass:{str fieldName: value}}
			
			where
			viewClass are views whose model has been setup,
			fieldName the public fields names
			value is the request value
			
			ONLY VALUED FIELDS ARE RECORDED
			
			}
		"""
		# getFieldsGroups returns the structure of public form
		fieldsGroups = self.getFieldsGroups()
		
		# values grouped by view
		viewFieldsValuesDictionary = {}
		
		# formatted user values
		fieldsValues = self.form.validate_all_to_request(REQUEST)
		
		for tableName in fieldsGroups:
			viewClass = self.models.getViewOfTable(tableName)
			viewFieldsValuesDictionary[viewClass] = {}
			for publicField in fieldsGroups[tableName]:
				fieldName = publicField.id
				value = fieldsValues[tableName+"_in_"+publicField.id]
				if value:
					viewFieldsValuesDictionary[viewClass][fieldName] = value
		
		return viewFieldsValuesDictionary
			
	security.declareProtected(View,'getFieldsGroups')
	def getFieldsGroups(self):
		""" returns a dictionary of table_names and the list of public fields related to """
		
		if not self.isUpdate() or not hasattr(self,"_fieldsGroups"):
			publicFieldsList = self.getPublicFieldsList()
			self._fieldsGroups = {}
			for field in publicFieldsList:
				try:
					self._fieldsGroups[publicFieldsList[field]].append(field)
				except KeyError:
					self._fieldsGroups[publicFieldsList[field]] = [field]
		
		return self._fieldsGroups
			
	'''

	'''	
	 # ######################################################################
	security.declareProtected(View,'contextFieldsList')
	def contextFieldsList(self,parametre=[]):
		"""
		renvoit la liste des champs de form correspondant aux id de champs et de groupes en parametre, qui est une chaine ou une liste de chaines
		s'il n'y a pas de parametre, renvoit tous les champs de form ou tous les champs du groupe contextuel
		"""
		
		context=self
		# GESTION DES PARAMETRES SPECIAUX
		
		# pas de parametre : tous les champs
		if not(parametre):
			# est on dans une sequence... 
			if hasattr(context,'sequence-item'):
				# et l'iteration correspond-elle a un nom de groupe ?
				group = getattr(context,'sequence-item')
				
				if group in [group.getId() for group in context.form.get_groups()]:
					# si oui on recupere l'id du groupe et on en fait le parametre
					parametre = [group.getId()]
				
				else:
					# sinon, alors on renvoit tous les champs
					return context.form.get_fields() 
			else:
				return context.form.get_fields()
		
		
		# si le parametre contient une chaine, alors on la considere comme une liste contenant uniquement cette chaine
		elif outils.same_type(parametre,""):
			parametre = [parametre]
		
		
		# CONSTRUCTION DE LA LISTE
		
		FieldList = []
		
		# si le parametre contient une liste, on renvoit la liste tous les champs dont l'id est dans cette liste
		
		if outils.same_type(parametre,[]):
			for idGroupOrField in parametre:
			# si l'element de la liste est un nom de champ, on ajoute le champ
				if idGroupOrField in context.form.get_field_ids():
					FieldList.append(context.form.get_field(idGroupOrField))
				# si l'element de la liste est un nom de groupe, on ajoute les champs du groupe
				elif idGroupOrField in [group for group in context.form.get_groups()]:
					for group \
					  in [group for group in context.form.get_groups() if group == idGroupOrField]:
						FieldList = FieldList + context.form.get_fields_in_group(group)
						break
			
		return [field.getId() for field in FieldList]
	
	security.declareProtected(View,'fieldNamesStrList')
	def fieldNamesStrList(self):
		""" returns a string of the request field names separated by commas (for sql request) """
		NamesStrList = ""
		for field in self.form.get_fields()[:-1]:
			NamesStrList += field.getId()+","
			
		NamesStrList += self.form.get_fields()[-1].getId()
		return NamesStrList

				
	
	
	'''
	security.declareProtected(View,'entryRequest')
	def entryRequest(self,currentResult):
		""" builds a link towards an entry from the current results row """
		
		pkeys = self.getPkeys() # list of primary keys of the current table
		
		httpRequest = self.absolute_url()+'?'
		
		
		for pkey in pkeys:
			httpRequest += pkey+"="
			httpRequest += str(currentResult[pkey])+"&"
		
		httpRequest+="entry_submission=1"
		
		return httpRequest
	'''			
	
	'''			
	def getFormType(self):
		""" gets form type (add form, search form, etc)"""
		return "publicForm"
	'''
	
	def getFormMessage(self):
		""" gets form message, for buttons, titles... """
		return "Submit"
	
	
		
	# #######################################################
	# 		FUNCTIONAL CUSTOMIZATION		#
	# #######################################################
	

	# ############# SET DEFAULT
	
	security.declareProtected(AddInraProjectManager,"setDefault")
	def setDefault(self,REQUEST=None):
		""" delete customization of 'customize' (in request) by deleting the object """
				
		if  REQUEST.form.has_key('customize'):
			customize = REQUEST.form['customize']
			self.manage_delObjects([customize])
			message = customize+" has been deleted"
		else:
			message = customize+" was not customized"
		REQUEST.response.redirect(self.absolute_url()+"?portal_status_message="+message)
	
	# ########## Edit customized method
	
	security.declareProtected(AddInraProjectManager,"setCustomized")
	def setCustomized(self,REQUEST=None):
		""" edits the body of customized method """
		customize = REQUEST.form['customize']
		customizedBody = REQUEST.form['customizedBody']
		
		set_method = getattr(self,"setCustomized_"+customize)
		message = set_method(customizedBody) # executes the set method for this customized method
		
		REQUEST.response.redirect(
			self.absolute_url()+"/customize_form?customize="+customize+"&portal_status_message="+message)
			
			
	# ############ create customized method :
	# related to method
	
	
	# ############### SQL REQUEST MANAGEMENT #############################

	_SQLRequestName = "searchFormZSQL" # name of the request
	
	
	def getSQLText(self,**kwargs):
			return self.getSQLSearchRequest()(src__=1,**kwargs)
			

	def getSQLResults(self,**kwargs):
		#REQUEST.form['numero']
		return self.getSQLSearchRequest()(**kwargs)
	

	security.declareProtected(View,'getSQLRequest')
	def getCreateProjectSQLRequest(self,**kwargs):
		""" gets the SQL Search Request associated to this form : 
			the main SQL Request for search request
			or the entry request for modification requests """
		
		
		if not self._fieldsListRequest: # caches the request
				self._fieldsListRequest = FSZSQLMethod(self,DB_TABLE_FIELDS_ZSQLFile)
				self._fieldsListRequest.connection = self.connection
		
		# if search request has been customized
		if "SQLRequest" in self.objectIds():
			request = self.SQLRequest
		else:
			request = getattr(self,self._SQLRequestName)
		if self.isSQLSecure(request.document_src()):
			return request
		
	def executeModifRequest(self,**kwargs):
		""" executes the modification request """
		return self.getSQLModifRequest()(**kwargs)
			
	def getSQLModifRequest(self,**kwargs):
		""" gets the SQL Modif Request associated to this form (works for each form type) """
		if "SQLRequest" in self.objectIds():
			request = self.SQLRequest
		else:
			request = getattr(self,self._SQLRequestName)
		if self.isSQLSecure(request.document_src()):
			return request
		

	security.declarePublic('isSQLSecure')
	def isSQLSecure(self,requestText):
		""" returns true if SQL is 'secure'
		 BUT ITS ONLY ERGONOMY : ONLY SECURING WITH CONNECTION STRING IS SECURE """
		
		return True
	
	security.declareProtected(AddInraProjectManager,'getSQLRequest')
	def customizeSQLRequest(self,REQUEST=None):
		""" action : copy the sql request into the forms manager and make it editable by user """
		if not("SQLRequest" in self.objectIds()):
			defaultSQL = getattr(self,self._SQLRequestName)
			template = defaultSQL.document_src().replace("<params></params>","")
			self.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod("SQLRequest","publicFormRequest",connection_id="connection",arguments="",template=template)
			
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=SQLRequest&portal_status_message=custom SQL Request has been added")

		
	security.declareProtected(AddInraProjectManager,'setSQLRequest')
	def setCustomized_SQLRequest(self,SQLRequestText):
		""" sets the sqlrequest from form """
		SQLRequestText = SQLRequestText.replace("<params></params>","")
		if self.isSQLSecure(SQLRequestText):
			self.SQLRequest.manage_edit(template=SQLRequestText,title=self.SQLRequest.title,arguments='',connection_id="connection", dtpref_cols='', dtpref_rows='')
			return "SQL Request has been saved"
			pass
		else:
			raise "Forbidden Request"

	security.declareProtected(View,"getZSQLTypeOfField")
	def getZSQLTypeOfField(self,field):
		""" gets the ZSQL type working with field """
		if type(field) == type(""):
			field = getattr(self.references,self.tableName).get_field(field) # if string, gets the reference field of that name
		return self._FormType2ZSQLType[field.meta_type]
		
	# ##################### scripts management ###################
	
	# customize
	security.declareProtected(AddInraProjectManager,"customizepost_script_project")
	def customizepost_script_project(self,REQUEST=None):
		""" action : copy the post_script_project into the forms manager and make it editable by user """
		message = self._customizeScript("post_script_project",params="request,results")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=post_script_project&"+message)
	
	security.declareProtected(AddInraProjectManager,"customizepre_script_project")
	def customizepre_script_project(self,REQUEST=None):
		""" action : copy the pre_script_project into the forms manager and make it editable by user """
		message = self._customizeScript("pre_script_project",params="")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=pre_script_project&"+message)
	
	security.declareProtected(AddInraProjectManager,"_customizeScript")
	def _customizeScript(self,scriptName,params=""):
		message=""
		if not(scriptName in self.objectIds()): # if no scriptname script in current form manager
			defaultscript = getattr(self,scriptName) # gets the first script acquired
			scriptBody = defaultscript.body()
			script = PythonScript(scriptName)
			script.ZPythonScript_edit(params=params,body=scriptBody)
			script.write(scriptBody)
			self._setObject(scriptName,script)
			message+="portal_status_message=custom "+scriptName+" has been added"+scriptBody
			
		return message
		
	# edit custom
	security.declareProtected(AddInraProjectManager,"setCustomized_pre_script_project")
	def setCustomized_pre_script_project(self,customizedBody):
		return self._setCustomizedScript(name="pre_script_project",params="",body=customizedBody)
		
	security.declareProtected(AddInraProjectManager,"setCustomized_post_script_project")
	def setCustomized_post_script_project(self,customizedBody):
		return self._setCustomizedScript(name="post_script_project",params="request,results",body=customizedBody)
		
	def _setCustomizedScript(self,name=None,params=None,body=None):
		script = getattr(self,name) # gets the first script acquired
		body=str(body).replace("\r","")
		script.write(body)
		
		return "custom "+name+" has been saved"
		
	# ####################### Templates management
	
	security.declareProtected(AddInraProjectManager,"customizepublicForm_body")
	def customizepublicForm_body(self,REQUEST=None):
		""" action : copy the post_script_project into the forms manager and make it editable by user """
		message = self._customizeTemplate("form_body")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=publicForm_body&"+message)
		
		
	security.declareProtected(AddInraProjectManager,"_customizeTemplate")
	def _customizeTemplate(self,name):
		message=""
		if not(name in self.objectIds()): # if no scriptname script in current form manager
			defaultTemplate = getattr(self,name) # gets the first script acquired
			defaultBody = defaultTemplate.document_src()
			template = DTMLMethod(name)
			template.manage_edit(data=defaultBody,title=name)
			self._setObject(name,template)
			message+="portal_status_message=custom "+name+" has been added"
			
		return message
	
	security.declareProtected(AddInraProjectManager,"setCustomized_publicForm_body")	
	def setCustomized_publicForm_body(self,customizedBody):
		return self._setCustomizedTemplate(name="publicForm_body",params="",body=customizedBody)

	def _setCustomizedTemplate(self,name=None,params=None,body=None):
		template = getattr(self,name) # gets the first script acquired
		body=str(body).replace("\r","")
		template.manage_edit(data=body)
		return "custom "+self.labelFromId(name)+" has been saved"		
		
		
	# #######################################################################	
	# ############### REQUEST FIELDS AND FORM CREATION ######################
	
	security.declareProtected(AddInraProjectManager,'setRequestFields')
	def setRequestFields(self,requestFields):
		""" sets the request fields : copy the new fields from reference, 
		 and delete the unselected ones """
		
		
		
		# deleting unselected fields
		form = self.form
		for field in form.get_fields():
			if not(field.id in requestFields):
				form.manage_delObjects([field.id])
		
		# evite un bug incomprehensible : un tuple vide se met dans requestFields
		self.requestFields = tuple([requestField for requestField in requestFields if requestField])
			
		if requestFields:
			self._copyReferenceFields()
		
	

		
	
registerType(PublicProjectForm)
