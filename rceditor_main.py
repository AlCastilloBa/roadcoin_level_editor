#!/usr/bin/env python3


import logging
import sys
import gettext

import rceditor_user_interface


if __name__ == "__main__":
	# Configure logger
	log = logging.getLogger()
	#log.setLevel(logging.DEBUG)
	log_handler = logging.StreamHandler(sys.stdout)
	log_handler.setLevel(logging.DEBUG)
	log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	log_handler.setFormatter(log_formatter)
	log.addHandler(log_handler)

	debugmode = False

	# Parse command line arguments
	for argument in sys.argv[1:]:	# Argument 0 is program name
		if argument == "--help":
			print( "Usage: rceditor_main [options] " )
			print( "Options: ")
			print( "  --help      Print this help text. ")
			print( "  --debug     Run the program with debug level log messages. ")
			print( "              Adds additional menus for debug purposes. ")
			sys.exit(0)
		elif argument == "--debug":
			log.setLevel(logging.DEBUG)
			debugmode = True
		else:
			print( "Unknown option: " + argument )
			sys.exit(0)


	log.debug("Programa iniciado")

##	# Set the local directory
##	localedir = './locale'
##	# Set up your magic function _()
##	translate = gettext.translation('rceditor', localedir, fallback=True)
##	_ = translate.gettext

	main_window_editor = rceditor_user_interface.RC_editor_GUI( debugmode )

	main_window_editor.MainWindowLoop()
