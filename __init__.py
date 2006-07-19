import sys

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, ManagePortal
from Products.CMFCore import utils
from Products.Archetypes.public import process_types, listTypes

from config import *
from permissions import *

import content

#from Products.CMFCore import utils

this_module = sys.modules[__name__]

product_globals=globals()

# make the skins available as DirectoryViews
registerDirectory(SKINS_DIR,globals())
registerDirectory(SKINS_DIR+"/"+PROJECTNAME,globals())
#registerDirectory('SQLRequests',globals())


#contentConstructors = (PloneDbFormsManager.addPloneDbFormsManager,)
#contentClasses = (PloneDbFormsManager.PloneDbFormsManager,)

def initialize(context):


	## archetypes initialization
	
	content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),PROJECTNAME)

	utils.ContentInit(
		"InraProjectsManager Content",
		content_types = content_types,
		permission = ManagePortal,
		extra_constructors = constructors,
		fti = ftis,).initialize(context)	

	
        context.registerClass(
            meta_type = content.ProjectViewModelsManager.ProjectViewModelsManager.archetype_name,
            constructors = (content.ProjectViewModelsManager.addProjectViewModelsManager,),
            permission = ADD_MANAGER_PERMISSION,
            )

        context.registerClass(
            meta_type = content.InraProjects.InraProject.archetype_name,
            constructors = (content.InraProjects.addInraProject,),
            permission = ADD_CONTENT_PERMISSION,
            )

        context.registerClass(
            meta_type = content.InraProjectsManager.InraProjectsManager.archetype_name,
            constructors = (content.InraProjectsManager.addInraProjectsManager,),
            permission = ADD_MANAGER_PERMISSION,
            )
	    
        context.registerClass(
            meta_type = content.ProjectViewModels.ProjectViewModel.archetype_name,
            constructors = (content.ProjectViewModels.addProjectViewModel,),
            permission = ADD_MANAGER_PERMISSION,
            )
	pass