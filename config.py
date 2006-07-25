from permissions import *

PROJECTNAME = "InraProjectsManager"
SKINS_DIR = 'skins'

ADD_MANAGER_PERMISSION = AddInraProjectManager
ADD_CONTENT_PERMISSION = AddInraProjects
GLOBALS = globals()

DB_TABLES_LIST_ZSQLFile = 'InraProjectsManager/SQLRequests/DBTablesList.zsql' # list of all db tables
DB_TABLE_FIELDS_ZSQLFile = 'InraProjectsManager/SQLRequests/DBTableFields.zsql' # list of fields of a table, with Type and Not null information TODO : UNIQUE, width

CONFIDENTIALITY_LEVELS = (
	("private","Réservé à l'équipe"),
	("protected","Réservé à la plateforme"),
	("public","Public"),
	 )

LIVE_LEVELS = (
	("archive","archived"),
	 ("live","in live"),
	  ("trash","in trash"),
	   ("test","test project"),
	    )
	   

DB_TYPE_TO_LEN = {
		'bool':1,
		'char':1,
		'name':64,
		'int8':8,
		'int2':2,
		'int2vector':64,
		'int4':4,
		'line':32,
		'float4':4,
		'float8':8,
		'money':4,
		'time':8,
		'text':None,
		'varchar':None,
		'date':None,
		'oid':8}
		
			# form types lists corresponding to db field types
FORM_TYPES_OF_DB_TYPES = {
		'int4':["IntegerField"],
		'int2':["IntegerField"],
		'bool':["CheckBoxField"],
		'oid':["IntegerField","StringField","PatternField","ListField","RadioField"],
		'char':["StringField","PatternField","RadioField","ListField"],
		'text':["StringField","TextAreaField","LinkField",
           "PasswordField","PatternField","RadioField","ListField","RawTextAreaField",
	   "EmailField","FileField"],
	   	'varchar':["StringField","PasswordField","PatternField","RadioField","ListField",
	   "EmailField","FileField"],
	   	'date':["DateTimeField"],
		'float4':["FloatField"],
		'float8':["FloatField"],
	}