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
	
	def getPublicRequestFieldsList(self):
		""" the list of request view fields used in public request form """
		pass
	
	def setRequestForm(self):
		""" sets the public request form """
		pass
	
	def getManagedViewsList(self):
		""" list of views on the projects managed by this projects manager """
		pass
	
	def addConnection(self,connection_info):
		""" creates a connection to a database """
		pass
	
	def majConnection(self,connection_info):
		""" updating the connection informations """
		pass
	
	def getInraProjects(self,):
		""" the list of projects actually stored """
	
	def addInraProject(self,REQUEST):
		""" adds a project (from requestForm) """
	
		
	def executeRequestForm(self,):
		""" manages displaying, submission, validation, treatment of the form provided to public. always returns XHTML code. uses requestView model with publicRequestFieldsList """
	
	def setupRequestForm(self,):
		""" creates or updates the public request form """
		pass
		
class IInraProject(Base):
	""" Provides an object that manages a project """
	
	
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
	
class IProjectView(Base):
	""" abstract class interface.
	a projectView subclass instance provides a view on an aspect of the project : project definition, ressources, reports, etc 
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
		""" returns a list of tuples
		(model,isSetup), containing each model listed in managedViewsList, with isSetup = True if the model has been setup, and else isSetup = False """
	
	def getViewDbTables(self,):
		""" returns the list of the tables in the database that corresponds to a view managed by this product """
	
	def getDbTablesList(self,):
		""" returns the list of database tables """

		
class IProjectViewModel(Base):
	""" contains information about the database table structure of a view, and its representation in the InraProjectsManager context :
	a dictionnary of the table structure
	a form - each field corresponding to a field of that table
	templates for displaying the view informations
	
	and tools to manage them
	"""
	
	def addProjectViewModelsManager(self):
		""" adds the models manager at self.model """
	
	def getTableName(self):
		""" gets the database table name for this view """
	
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
	
	def createForm(self):
		""" creates the form from view properties """
		pass
