from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.DirectoryView import addDirectoryViews
#from Products.CMFCore.TypesTool import ContentFactoryMetadata

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.InraProjectsManager import product_globals 
from Products.InraProjectsManager.workflows import activate_deactivate_workflow, project_workflow

from Products.InraProjectsManager.config import *

def install(self):
	"""Register skin layer with skin tool, and other setup in the future """
	
	out = StringIO() # setup stream for status messages
	
	out.write(install_archetypes_types(self))
	
	out.write(install_archetypes_skins(self))
	
	out.write(install_workflow(self))
	

	cssreg = getToolByName(self, 'portal_css', None)

        if cssreg is not None:
            stylesheet_ids = cssreg.getResourceIds()
            # Failsafe: first make sure the two stylesheets exist in the list
            if 'plonedbformulator.css' not in stylesheet_ids:
                cssreg.registerStylesheet('plonedbformulator.css')

            # Failsafe: first make sure the two stylesheets exist in the list
            if 'inraprojectsmanager.css' not in stylesheet_ids:
                cssreg.registerStylesheet('inraprojectsmanager.css')

	return out.getvalue()

def install_archetypes_skins(self):
	out = StringIO()
	out.write(install_subskin(self,out,GLOBALS))
	return out.getvalue()

def install_archetypes_types(self):
	# Install Archetypes types
	out = StringIO()
	out.write(installTypes(self,out,listTypes(PROJECTNAME),PROJECTNAME))
	return out.getvalue()	

def install_workflow(self):
	out=StringIO()
	
	wf_tool = getToolByName(self,'portal_workflow',None)
	
	# install and add activate_deactivate_workflow
	activate_deactivate_workflow.install()
	if not 'activate_deactivate_workflow' in wf_tool.objectIds():
		wf_tool.manage_addWorkflow(workflow_type='activate_deactivate_workflow (Activate Deactivate Workflow)',
					id='activate_deactivate_workflow')
	wf_tool.setChainForPortalTypes(('InraProjectsManager','PublicProjectForm'),'activate_deactivate_workflow')
	out.write("activate_deactivate_workflow installed")
	
	# install and add project_workflow
	project_workflow.install()
	if not 'project_workflow' in wf_tool.objectIds():
		wf_tool.manage_addWorkflow(workflow_type='project_workflow (Project Workflow)',
					id='project_workflow')
	wf_tool.setChainForPortalTypes(('InraProjects'),'project_workflow')
	out.write("project_workflow installed")
	
	wf_tool.updateRoleMappings()
	
	return out.getvalue()
	
def uninstall(self):
	out = StringIO()
	
	return out.getvalue()

