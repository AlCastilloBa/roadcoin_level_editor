import gettext
import os
import logging


supported_languages = ["es","en","fr"]


def Initialize_Translations_Language( language ):
	# This function initializes the language, and returns the function that should be mapped to the "_" function.
	# example: _ = rceditor_lang.Initialize_Translations_Language( "en" )

	global current_language
	global current_gettext_function
	current_language = language

	localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
	translate = gettext.translation('rceditor', localedir, fallback=True)

	if language is not None:
		if language == "es":
			es = gettext.NullTranslations()
			es.install()		# Install _ in Pyhton built-in namespace
			logging.debug("Seleccionado idioma del programa: es")
			current_gettext_function = es.gettext
			return translate.gettext
		elif language == "en":
			en = gettext.translation('rceditor', localedir, languages=['en'])
			en.install()		# Install _ in Pyhton built-in namespace
			logging.debug("Chosen application language: en")
			current_gettext_function = en.gettext
			return en.gettext
		elif language == "fr":
			fr = gettext.translation('rceditor', localedir, languages=['fr'])
			fr.install()
			logging.debug("Langue du programme selectionee: fr")
			current_gettext_function = fr.gettext
			return fr.gettext
		else:
			logging.error("Error: el idioma " + language + " no esta admitido por el programa. Se utilizara el idioma por defecto.")
			current_gettext_function = translate.gettext
			return translate.gettext
	else:
		logging.error("Error: no se ha especificado un idioma. Se utilizara el idioma por defecto.")
		es = gettext.NullTranslations()
		es.install()
		current_gettext_function = es.gettext
		return translate.gettext

def Get_Current_Language():
	# This function returns the name of the current language already initialized
	return current_language

def Get_Current_Gettext_Function():
	# This function returns the function (already initialized) that should be mapped to the "_" function.
	# Example: _ = rceditor_lang.Get_Current_Gettext_Function()
	#
	# If _ is installed in built-in namespace, then this function is not needed
	return current_gettext_function

