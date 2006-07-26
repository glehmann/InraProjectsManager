from Interface import Base

# putators, mutators and getters of attributes are provided by archetypes

class IInraProjectsManager(Base):
	""" provides objects that manages the projects of one type in INRA """
	
	def getConnection(self): 
		""" a Z connecter to the projects database """
		pass
	
	def getConnectionInfo(self):
		""" the connection string to the database"""
		pass
	
	# ############## 
	
	def getManagedViewsList(self):
		""" list of views on the projects managed by this projects manager """
		pass
	
	# ############# CONNECTION
	
	def addConnection(self,connection_info):
		""" creates a connection to a database """
		pass
	
	def majConnection(self,connection_info):
		""" updating the connection informations """
		pass
	
	def getInraProjects(self,):
		""" the list of projects actually stored """
		

	# ############## PUBLIC FORM MANAGEMENT
		

	def getPublicForm(self):
		""" gets the public form manager at self.publicForm, creates if not exists """
	
	def getProjectViewModelsManager(self,):
		""" gets the models manager of this project manager """
	

	# ########## MODELS
	
	def getSetupModels(self):
		""" returns the list of models that have been setup """	
	
	
	# ########### PROJECTS CREATION
		
	def realize_publicForm_submission(self,viewFieldsValuesDictionary):
		""" executes the treatment of submission form by the creation of a new project """
	
	def addInraProjectDbEntry(self,REQUEST=None,**kwargs):
		""" adds the entry of a new project in the database from the public form request datas
		 returns the int projectId
		 """
		 
	def getNextProjectId(self):
		""" returns the value of next project id in the database - inra_projects table """
			
	def createInraProject(self,projectId,person_in_charge,customer_in_charge,viewFieldsValuesDictionary):
		""" creates the inra project with id projectId managed by person_in_charge, 
		with the publicForm datas stored in viewFieldsValuesDictionary """
		
class IInraProject(Base):
	""" Provides an object that manages a project """
	
	
	def getState(self):
		""" the state of the project : , working, refused, aborted, finished"""
		
	def getLiveLevel(self):
		""" the state of the project document : live, archive, test or trash """
	
	def getConfidentiality(self):
		""" the confidentiality level : public, inra, confidential"""
	
	
	def getProjectDbKey(self,):
		""" gets the identifier of that project in the database """
	
	def initProjectViews(self,viewFieldsValuesDictionary):
		""" creates the views of the project and feed them with public form values """
		pass
	
	def getView(self,viewNameStr):
		""" gets the view viewNameStr """
		pass
	
	def getViews(self):
		""" returns the dict of views """
		
class IProjectView(Base):
	""" abstract class interface.
	a projectView subclass instance provides a view on an aspect of the project : project definition, ressources, reports, etc. 
	it is a set of functionnalities for the management of the TableName database table
	each view type may have its particular class
	
	"""
	
	def getModel(self,):
		""" gets the model for this view, defined in the context of a InraProjectsManager instance 
		"""
		pass
	
	def getProjectViewId(self,):
		""" gets the identifiers (a tuple key, value) of that view of that project in the view table """
		
	def executeForm(self,**context):
		""" manages displaying, submission, validation, treatment of the form of that view in the context of this project. always returns XHTML code """
	
	def getTableName(self):
		""" gets the table of that view """
		pass
	
		
class IProjectViewModelsManager(Base):
	""" contains and manages the data models of the project type managed by this projectsManager 
	"""
	
	def getModelsList(self,):
		""" returns a dict str model : boolean isSetup, containing each model listed in managedViewsList, with isSetup = True if the model has been setup, and else isSetup = False """
	
	def getViewDbTables(self,):
		""" returns the list of the tables in the database that corresponds to a view managed by this product """
	
	def getViewOfTable(self,tableName):
		""" returns the view which table is named tableName """
		
	def getDbTablesList(self,):
		""" returns the list of database tables """

	def getModel(self,modelName):
		""" returns the ProjectViewModel object modelName """
		
	def edit_model(self,modelName,**kwargs):
		""" displays the model manager """
		
	def getModelOfTable(self,tableName):
		""" returns the model which table_name is named tableName """
		
class IProjectViewModel(Base):
	""" contains information about the database table structure of a view, and its representation in the InraProjectsManager context :
	a dictionnary of the table structure
	a form - each field corresponding to a field of that table
	templates for displaying the view informations
	
	and tools to manage them
	"""
	
	""" viewModel are customization
	    viewClass are functional
	"""
	
	def addProjectViewModelsManager(self):
		""" adds the models manager at self.model """
	
	def getTableName(self):
		""" gets the database table name for this view """
	
	def getViewClass(self):
		""" gets the view class related to this view model """
		
	def getDbTableStructure(self,):
		""" returns a dictionnary of dictionnaries containing the structure of the table. :
			
		{str fieldName:{str: property:value}}
		
		properties are at least : label, width, type
		"""
	
	def setViewProperties(self,REQUEST=None):
		""" """
		pass
	
	def editViewProperties(self,REQUEST=None):
		""" """
		pass
	# ######## PUBLIC FORM : this class provides management for the fields that are used on public form

class IPublicProjectForm(Base):
	""" The object that manages the form that creates a project """
	
		
	# ####### METHODS RELATED TO FIELDS SELECTION
	
	def isViewOnPublicForm(self):
		""" returns true if view fields can be used on public form """
	
	def isFieldOnPublicForm(self,fieldName):
		""" returns true if view fields can be used on public form """
	
	def setFieldOnPublicForm(self,viewName,fieldName):
		""" puts or updates the field on public form """
		
	def getFieldsOnPublicForm(self):
		""" gets the list of fields of that model to be used on public form """	
		
	def isUpdate(self):
		""" returns true if project form is up to date """
	
	# ####### PUBLIC FORM MANAGEMENT
	def updateForm(self):
		""" creates and updates the public form, using hard-coded fields and dynamical user fields of models """
		
	def setUnupdated(self):
		""" sets that the form has to be updated to be conform to new configurations """
	
	# ########## PUBLIC FORM EXECUTION	
	
	def execute_form(self):
		""" validates the form, executes prescript, request and post script. creates a new project if necessary """
	
	def getPublicFieldsList(self):
		""" returns the list of public form fields as a dictionary object field : str table_name """
		
	def updateModelField(self,field):
		""" copy model fields into the publicForm. old ones are just updated except if their type has changed """

	pass