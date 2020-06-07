#!/usr/bin/env python3


import logging
import sys
import gettext

import rceditor_user_interface


if __name__ == "__main__":
	# Configure logger
	log = logging.getLogger()
	log.setLevel(logging.DEBUG)
	log_handler = logging.StreamHandler(sys.stdout)
	log_handler.setLevel(logging.DEBUG)
	log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	log_handler.setFormatter(log_formatter)
	log.addHandler(log_handler)

	log.debug("Programa iniciado")

	# Set the local directory
	localedir = './locale'
	# Set up your magic function _()
	translate = gettext.translation('rceditor', localedir, fallback=True)
	_ = translate.gettext

	main_window_editor = rceditor_user_interface.RC_editor_GUI()

	main_window_editor.MainWindowLoop()
