#
# PloneTestCase API
#

# $Id: ptc.py 23729 2006-05-18 22:09:24Z hannosch $

from Testing.ZopeTestCase import hasProduct
from Testing.ZopeTestCase import installProduct

from Testing.ZopeTestCase import Sandboxed
from Testing.ZopeTestCase import Functional

from Testing.ZopeTestCase import utils
from Testing.ZopeTestCase.utils import *

from Products.PloneTestCase.setup import PLONE21
from Products.PloneTestCase.setup import PLONE25
from Products.PloneTestCase.setup import portal_name
from Products.PloneTestCase.setup import portal_owner
from Products.PloneTestCase.setup import default_policy
from Products.PloneTestCase.setup import default_products
from Products.PloneTestCase.setup import default_extension_profiles
from Products.PloneTestCase.setup import default_user
from Products.PloneTestCase.setup import default_password

from Products.PloneTestCase.setup import setupPloneSite

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase

