from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
from Products.Formulator import Form

from Products.InraProjectsManager.interfaces import IProjectViewModel
from Products.InraProjectsManager.permissions import *
from Products.InraProjectsManager.config import *
from Products.InraProjectsManager import outils
import ProjectViews

def addProjectViewModel(self,id,REQUEST=None,**kwargs):
	""" adds an Inra View Model """
	object = ProjectViewModel(id,**kwargs)
	self._setObject(id, object)


factory_type_information = (
	{ 'id':'ProjectViewModel',
	 'meta_type':'ProjectViewModel',
	  'description':'The model of a view',
	   'content_icon':'formmanager.gif',
	    'product':'InraProjectsManager',
	     'filter_content_types':True,
	      'allowed_content_types':(),
	      'global_allow':False,
	     'factory':'addProjectViewModel',
	      'default_view':'view',
	      'view_methods':('view'),
	      'immediate_view':'fields_properties',
	      
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'model_fields_properties_form',
		 	'permissions':(AddInraProjectManager,),
			},
			
		),

	   'aliases':(
	    	{
	     	'edit':'atct_edit',
		'view':'model_fields_properties_form',
		}),

	},
)

#  

ProjectViewModelSchema = Schema((
	
	   ))

	
class ProjectViewModel(OrderedBaseFolder):
	""" contains information about the database table structure of a view, and its representation in the InraProjectsManager context :
	a dictionnary of the table structure
	a form - each field corresponding to a field of that table
	templates for displaying the view informations
	
	and tools to manage them
	"""
	
	__implements__ = (IProjectViewModel,)
	
	archetype_name="Project View Model"
	
	schema = OrderedBaseFolder.schema + ProjectViewModelSchema
	
	security = ClassSecurityInfo()
	
	_deleteCache = False
	
	_DbTableStructure = None
	_fieldsListRequest = None # the zsql request for the table fields 
	
	
	
	security.declareProtected("getTableName",View)
	def getTableName(self):
		""" gets the database table name for this view """
		if not hasattr(self,"_tableName") or self._deleteCache:
			self._tableName = self.getViewClass()._tableName
		return self._tableName
	
	security.declareProtected("getViewClass",View)
	def getViewClass(self):
		""" recupere la classe de la vue du modele courant
		 in our implementation the model instance has the same name has the view class """
		if not hasattr(self,"_viewClass") or self._deleteCache:
			self._viewClass = getattr(ProjectViews,self.getId())
		return self._viewClass
		
	
	# ################################### TABLE STRUCTURE ######################
	
	security.declareProtected("getDbTableStructure",AddInraProjectManager)
	def getDbTableStructure(self,):
		""" returns a dictionary of dictionaries containing the structure of the table. :
			
		{str fieldName:{str property:value}}
		
		properties are at least : str label, int width, str type, bool userField, bool null
		
		userField : userField fields are fields of projects manager choice
		
		systemField : systemField fields are fields unuseful to users
		
		DbTableStructure is cached in self._DbTableStructure - initDbTableStructureSave initializes it
		
		"""
		
		
		if not self._DbTableStructure:
		
			self._DbTableStructure = {}
			
			if not self._fieldsListRequest: # caches the request
				self._fieldsListRequest = FSZSQLMethod(self,DB_TABLE_FIELDS_ZSQLFile)
				self._fieldsListRequest.connection = self.connection
				#_fieldsListRequest.connection.manage_open_connection()
			
			tableName = self.getTableName()
			
			fieldsListResult = self._fieldsListRequest(tableName=self.getTableName())
			
			
			for field in fieldsListResult:
				fieldId = field['field']
				fieldDefs = {}
				fieldDefs['userField'] = fieldId.startswith('_') 
				fieldDefs['systemField'] = fieldId.startswith('__')
				#fieldDefs['foreign_key'] = False # TODO
				#fieldDefs['auto_num'] = False # TODO
				fieldDefs['width'] = DB_TYPE_TO_LEN[field['type']]
				fieldDefs['null'] = field['not_null']
				fieldDefs['type'] = field['type']
				#fieldDefs['unique'] = False # TODO
				fieldDefs['label'] = outils.labelFromId(fieldId)
				fieldDefs['on_public_form'] = False

				
				self._DbTableStructure[fieldId]=fieldDefs
			
			#fieldslistRequest.connection.manage_close_connection()
			
			
		return self._DbTableStructure

	security.declareProtected("initDbTableStructureSave",AddInraProjectManager)	
	def initDbTableStructureSave(self,):
		""" """
		self._DbTableStructure = None
		return self.getDbTableStructure()
		
	# ############################################ FORMS ##################
	
	def isSetup(self):
		""" returns true if model is setup """
		return "form" in self.objectIds()
	
	def initializeForm(self,REQUEST=None):
		""" initializes the form from view properties and DbTableStructure """
		tableStructure = self.initDbTableStructureSave()
		
		if "form" in self.objectIds():
			self.manage_delObjects(["form"])
				
		if not(REQUEST==None):
			REQUEST.response.redirect(".")

	
	def createForm(self):
		self.initializeForm()
		Form.manage_add(self, "form", title="formulaire", unicode_mode=True)
		setattr(self.form,'stored_encoding',"UTF-8")
		self.form.manage_addProperty("fields_on_public_form",tuple(),"lines")
		self.initDbTableStructureSave()
					
	def setViewProperties(self,REQUEST=None):
		""" raz the form and rebuilds it with datas from request """
			
		parameters = REQUEST.form
		
		tableFields = self.getTablePropertiesFromRequest(REQUEST)
		
		
		# creation of the form model
		self.createForm()
		
		self._DbTableStructure = tableFields
		
		# the form contains a formulatorField by field
		
		for fieldName in tableFields:
			
			fieldProperties = tableFields[fieldName]
			
			#if not(fieldProperties.has_key('primary_key')): fieldProperties['primary_key']=False

			#if not(fieldProperties.has_key('auto_num')): fieldProperties['auto_num']=False
							
			if not(fieldProperties.has_key('null')): fieldProperties['null']=False
			if not(fieldProperties.has_key('width')): fieldProperties['width']=0
			if not(fieldProperties.has_key('on_public_form')): fieldProperties['on_public_form']=False
			
			self.addViewField(fieldName,
					fieldType=fieldProperties['type'],
					title=fieldProperties['label'],
					null=fieldProperties['null'])
			
			
			if self._DbTableStructure[fieldName]['on_public_form']:
				self.setFieldOnPublicForm(fieldName)
			else:
				self.unsetFieldOnPublicForm(fieldName)
				
			#print tableForm,field,fieldProperties['type'],fieldProperties['label']
		#return self._DbTableStructure
		
		self.getPublicForm().setUnupdated()
		
		REQUEST.response.redirect("..")
	
		
	def editViewProperties(self,REQUEST=None):
		""" updates the form with datas from request """
		
		#self.unsetFieldOnPublicForm('somme_demandee')
		#self.setFieldOnPublicForm('nom')
		#return "toto"
		tableFields = self.getTablePropertiesFromRequest(REQUEST)
		
			
	
		for fieldName in tableFields:
			
			fieldProperties = tableFields[fieldName]
			
			if not(fieldProperties.has_key('null')): fieldProperties['null']=False
			if not(fieldProperties.has_key('width')): fieldProperties['width']=0
			if not(fieldProperties.has_key('on_public_form')): fieldProperties['on_public_form']=False
		
			for property in fieldProperties:
				self._DbTableStructure[fieldName][property] = fieldProperties[property]
			
			#return str(fieldProperties)+'\n'+str(self._DbTableStructure[fieldName])
		
		
			if self._DbTableStructure[fieldName]['on_public_form']:
				
				self.setFieldOnPublicForm(fieldName)
			else:
				
				self.unsetFieldOnPublicForm(fieldName)

			self.editViewField(fieldName,
					title=fieldProperties['label'],
					null=fieldProperties['null'],
					width=fieldProperties['width'])
		
		self.getPublicForm().setUnupdated()
		
		REQUEST.response.redirect("..")
	
	
	def getTablePropertiesFromRequest(self,REQUEST):
		""" creates from request a dictionnary of fields and parameters {fieldName str:{fieldParameter str: parameterValue div}} """
		
		form = REQUEST.form
				
		tablePropertiesDicts = {}

		# parses the request datas

		for finput in form:
			# field parameters
			if finput.find('.')>-1:
				parameter = finput.split('.')
				fieldParam = parameter[0]
				paramParam = parameter[1]
				# parameter[0] : field name, parameter[1] : property, form[input] : param value
				
				
				if not(tablePropertiesDicts.has_key(fieldParam)):
					tablePropertiesDicts[fieldParam]={'label':outils.labelFromId(fieldParam)}
				
				# property value from parameter value :
				if paramParam in ["primary_key","null","auto_num","on_public_form"]:
					valueParam = True
				elif paramParam in ["width"]:
					if not form[finput]:
						valueParam=None
					else:
						valueParam = int(form[finput])
				else:
					valueParam = form[finput]
				
				tablePropertiesDicts[fieldParam][paramParam]=valueParam
		
		
		return tablePropertiesDicts
	
	def getFormTypesOfDBType(self,DBtype=""):
		""" gets form types list corresponding to db type management """
		if not(DBtype):
			return FORM_TYPES_OF_DB_TYPES
		if not type(DBtype) == type(""):
			raise TypeError
		if FORM_TYPES_OF_DB_TYPES.has_key(DBtype):
			return FORM_TYPES_OF_DB_TYPES[DBtype]
		else:
			raise str(DBtype)+" type is not managed by FORM_TYPES_OF_DB_TYPES. patch it if necessary"
				
	
			
	# ######## FIELDS / REFERENCE FIELDS	
	def addViewField(self,fieldName,
					fieldType="StringField",
					title="",
					primary_key=False,
					auto_num=False,
					null=False,
					width=8,
					unique=False):
		""" adds a reference field with those properties """
		
		if not(title):
			title = self.labelFromId(fieldName)
		
		if self.isDefaultDbField(fieldName): # permet la gestion des champs par defaut, commencant par underscore
			fieldName = "d"+fieldName
		
		self.form.manage_addField(fieldName,Form.convert_unicode(title),fieldType)
		field = getattr(self.form,fieldName)
		
		self._setFieldSettings(field,title=title,
					null=null,
					width=width)
		
	def editViewField(self,fieldName,
					title="",
					primary_key=False,
					auto_num=False,
					null=False,
					width=8,
					unique=False):
		""" adds a reference field with those properties """
		
		if not(title):
			title = self.labelFromId(fieldName)
		

		# build field properties from settings
		field = getattr(self.form,fieldName)
		
		self._setFieldSettings(field,title=title,
					null=null,
					width=width)
		
	
	def isDefaultDbField(self,dbFieldId):
		return dbFieldId.startswith('_')
	
	def isSystemDbField(self,dbFieldId):
		
		return dbFieldId.endswith('__')
	
	
	def isDefaultField(self,field):
		return field.getId().endswith('__')
	
	def isSystemField(self,field):
		return field.getId().endswith('__')
			
		
	
	# ######### A REVOIR !!!
	def _setFieldSettings(self,field,**kwargs):
		
		settingsDictionnary = {'required':kwargs.get('null',False),'title':kwargs.get('title',outils.labelFromId(field.__name__)),'unicode':True}
		
		width = kwargs.get('width',None)
		
		# VALIDATION CONSTRAINTS : a ameliorer !!!
		if width:
			if field.has_value('end'): # pour les entiers qui peuvent avoir un maximum
				settingsDictionnary['start']= 0 - (2 ** (2**width)) / 2 -1
				settingsDictionnary['end']= (2 ** (2**width)) / 2 +1
				settingsDictionnary['display_maxwidth'] = (2 ** (2**width))/10+1
	
			elif field.has_value('max_length'):
				settingsDictionnary['max_length'] = width
				if field.meta_type in ["TextAreaField","RawTextAreaField"]:
					settingsDictionnary['width']=40
					settingsDictionnary['height']=width/40+1
				else:
					settingsDictionnary['display_maxwidth'] = width
		
		'''
		primary_key = kwargs.get('null',False)
		
		if primary_key:
			# primary keys are stored as a reference form property
			#referenceFormObject.manage_changeProperties(
			#	{"primary_keys":referenceFormObject.primary_keys + (fieldName,)})
		'''
		
		unique = kwargs.get('unique',False)
		if unique: # TODO
			settingsDictionnary['external_validator']="verifyUnicityConstraint"
		
		auto_num = kwargs.get('auto_num',False)
		if auto_num:
			settingsDictionnary['override_default']="sequelAutoNum"
		
		for setting in settingsDictionnary:
			field.values[setting] = settingsDictionnary[setting]
	
			
			
	security.declareProtected(View,'getViewField')
	def getViewField(self,fieldName):
		""" returns the reference field 'fieldName' of table 'tableName' """
		
		return getattr(self.form, fieldName)
	
	security.declareProtected(View,'getFieldWidth')
	def getFieldWidth(self,tableName,fieldName):
		""" returns the field with, if set """
		fieldWidth = getattr(self.form, fieldName).db_width
		if fieldWidth:
			 return fieldWidth
		else:
			 return None
	
	# ######## PUBLIC FORM : this class provides management for the fields that are used on public form
		
	def isViewOnPublicForm(self):
		""" returns true if view fields can be used on public form """
		return self.getViewClass()._on_public_form
	
	def isFieldOnPublicForm(self,fieldName):
		""" returns true if view fields can be used on public form """
		if not hasattr(self.form,fieldName): raise AttributeError, "pas de champ" + fieldname
		return fieldName in self.form.fields_on_public_form
	
	def setFieldOnPublicForm(self,fieldName):
		""" sets the field as a field on public form """
		if not hasattr(self.form,fieldName): raise AttributeError, "pas de champ" + fieldname
		if not self.isFieldOnPublicForm(fieldName):
			self.form.fields_on_public_form += (fieldName,)
	
	def getFieldsOnPublicForm(self):
		""" gets the list of fields of that model to be used on public form """
		if not self.form.hasProperty("fields_on_public_form"): return []
		
		for public_form_field_name in self.form.fields_on_public_form:
			
			return [self.form.get_field(public_form_field_name) for public_form_field_name in self.form.fields_on_public_form]
		
		
	def unsetFieldOnPublicForm(self,fieldName):
		""" unsets the field as a field on public form """
		if not hasattr(self.form,fieldName): raise AttributeError, "pas de champ" + fieldName
		
		newList = tuple()
		
		if self.isFieldOnPublicForm(fieldName):
			
			for field in self.form.fields_on_public_form:
				if field != fieldName:
					newList += (field,)
		
			self.form.fields_on_public_form = newList
		
			
registerType(ProjectViewModel)