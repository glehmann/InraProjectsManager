#!/usr/bin/python *- encoding=utf-8 -*

import os, sys

if __name__ == '__main__':
	execfile(os.path.join(sys.path[0],'framework.py'))
	
from Products.PloneTestCase import PloneTestCase
import unittest

from utils import dict_cmp

from Products.InraProjectsManager.interfaces import *
from Products.InraProjectsManager.contents  \
	import ProjectViewModels, InraProjects, InraProjectsManager, ProjectViewModelsManager

class TestIInraProjectsManager(PloneTestCase.PloneTestCase):
	def test_interface(self,):
		testinterface = wellImplements(InraProjectsManager.InraProjectsManager,IInraProjectsManager)
		self.failUnless(testinterface[0],testinterface[1])
		
class TestIInraProject(PloneTestCase.PloneTestCase):
	def test_interface(self,):
		testinterface = wellImplements(InraProjects.InraProject,IInraProjects)
		self.failUnless(testinterface[0],testinterface[1])
	
class TestIProjectView(PloneTestCase.PloneTestCase):
	def test_interface(self,):
		testinterface = wellImplements(ProjectViews.ProjectView,IProjectView)
		self.failUnless(testinterface[0],testinterface[1])
		
class TestIProjectViewModelsManager(PloneTestCase.PloneTestCase):
	def test_interface(self,):
		testinterface = wellImplements(ProjectViewModelsManager.ProjectViewModelsManager,IProjectViewModelsManager)
		self.failUnless(testinterface[0],testinterface[1])
		
class TestIProjectViewModel(PloneTestCase.PloneTestCase):
	def test_interface(self,):
		testinterface = wellImplements(ProjectViewModels.ProjectViewModel,IProjectViewModel)
		self.failUnless(testinterface[0],testinterface[1])

def testinterface(implementation,interface):
	return interface.isImplementedByInstancesOf(interface)
		
def test_suite():
	""" permet de declarer la classe Test... comme une classe de test, et prepare pour l'ajout a la suite """
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestIInraProjectsManager))
	suite.addTest(unittest.makeSuite(TestIInraProject))
	suite.addTest(unittest.makeSuite(TestIProjectView))
	suite.addTest(unittest.makeSuite(TestIProjectViewModelsManager))
	suite.addTest(unittest.makeSuite(TestIProjectViewModel))
	return suite