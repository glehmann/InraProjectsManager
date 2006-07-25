## Script (Python) "pre script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
# SCRIPT S'EXECUTANT AVANT LA RECHERCHE, affiche le retour en haut de la page
# Variables contextuelles utiles :
form = context.publicForm.form                     # LE FORMULAIRE
formFieldsGroups = context.getFieldsGroups() # LISTE DES IDENTIFIANTS DES CHAMPS DU FORMULAIRE

REQUEST = container.REQUEST             # LA REQUETE
# VERIFIER LA VALEUR D'UNE REQUETE :
# ex. pour le champ toto
# valeurToto = REQUEST['toto']
# l'operateur est 'dbForm_op', le critere de tri est 'dbForm_order'
# MODIFIER LA VALEUR D'UN PARAMETRE D'UNE REQUETE
# REQUEST.set('toto','nouvelle valeur')
#REQUEST.set('dbForm_op','OR')
return ""