#
# Interface tests
#

# $Id: testInterfaces.py 21592 2006-03-30 18:06:54Z shh42 $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.interfaces import *

from Interface.Verify import verifyClass
from Interface.Verify import verifyObject


class TestPloneTestCase(PloneTestCase.PloneTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIProfiled(self):
        self.failUnless(verifyClass(IProfiled, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IProfiled, self))

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testIPloneTestCase(self):
        self.failUnless(verifyClass(IPloneTestCase, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPloneTestCase, self))

    def testIPloneSecurity(self):
        self.failUnless(verifyClass(IPloneSecurity, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPloneSecurity, self))


class TestFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIFunctional(self):
        self.failUnless(verifyClass(IFunctional, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IFunctional, self))

    def testIProfiled(self):
        self.failUnless(verifyClass(IProfiled, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IProfiled, self))

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testIPloneTestCase(self):
        self.failUnless(verifyClass(IPloneTestCase, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPloneTestCase, self))

    def testIPloneSecurity(self):
        self.failUnless(verifyClass(IPloneSecurity, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPloneSecurity, self))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneTestCase))
    suite.addTest(makeSuite(TestFunctionalTestCase))
    return suite

if __name__ == '__main__':
    framework()

