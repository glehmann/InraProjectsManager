#!/usr/bin/python
#
# Runs all tests in the current directory
#
# Execute like:
#   python runalltests.py
#
# Alternatively use the testrunner: 
#   python /path/to/Zope/utilities/testrunner.py -qa
#


import os, sys


os.environ.update({'SOFTWARE_HOME':"/usr/local/www/zope/lib/python",'INSTANCE_HOME':"/zope/test",'VERBOSE_TEST':"True"})


if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py')) 

import unittest

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

import Testing
import Zope2

Zope2.startup()

PloneTestCase.installProduct('Five')

PloneTestCase.installProduct('Formulator')

PloneTestCase.installProduct('ZPsycopgDA')
#PloneTestCase.setupPloneSite(products=('InraProjectsManager',))

TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test in tests:
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

if __name__ == '__main__':
    TestRunner().run(suite)

from datetime import datetime
endTest = datetime.now()
print endTest.ctime()