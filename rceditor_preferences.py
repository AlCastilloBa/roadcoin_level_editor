

import tkinter as tk
from tkinter import ttk		# Textbox
import logging


def do_nothing():
	x = 0


class Preferences():
	GamePath = None
	
	def LoadPreferences( self ):
		file1 = open( "./settings" , 'r' )
		Lines = file1.readlines()
		for idx, line in enumerate(Lines):
			# Strip newline and spaces
			line = line.strip()
			logging.debug( "Leida linea "+ str(idx) + ": " + line )
			# Find and strip remarks at the right side of " #"
			if line.find(" #") != -1:
				line = line.split(" #",1)[0]
			# Check if line is empty
			if line == "":
				logging.debug( "Linea vacia")
			# Check if first character is "#" --> This is a remark
			elif line[0] == '#':
				logging.debug( "This is a comment, nothing has to be done")
			elif len(line) == 0:
				logging.debug( "Empty line.")
			elif line.find("GamePath") != -1:
				self.GamePath = line.split("=",1)[1].strip()
				logging.debug( "Encontrado GamePath = " + self.GamePath )
			####################################################
			# Add new options at this point
			####################################################
			else:
				logging.debug( "Expresion no reconocida, se ignora" )	

		file1.close()




	def SavePreferences( self ):
		pass




#########################################################################3


class PreferencesWindow():
	preferences_ref = None		# Reference to preferences object

	def __init__( self, master , preferences ):
		self.preferences_ref = preferences

		self.PrefWindow = tk.Toplevel( master )
		self.PrefWindow.transient( master )		# Make this window be child of parent
		self.PrefWindow.grab_set()			# Make this window Modal
		self.PrefWindow.protocol('WM_DELETE_WINDOW',do_nothing)		# Close window button behaviour
		# self.PrefWindow.attributes('-topmost', 'true')		# Stay on top of all others
		self.PrefWindow.title("Preferencias...")

		self.label_game_path = tk.Label(master=self.PrefWindow,text="Ruta del juego:")
		self.textbox_game_path = ttk.Entry(master=self.PrefWindow, width = 15 )
		self.textbox_game_path.insert(0, preferences.GamePath)

		self.button_accept = tk.Button(master=self.PrefWindow, text="Aceptar", command = self.AcceptButton )
		self.button_cancel = tk.Button(master=self.PrefWindow, text="Cancelar", command = self.CancelButton )

		self.PrefWindow.columnconfigure( 0, weight=0, minsize=200)
		self.PrefWindow.columnconfigure( 1, weight=1, minsize=200)
		self.PrefWindow.rowconfigure( list(range(5)) , weight=0, minsize=10)

		self.label_game_path.grid( row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.textbox_game_path.grid( row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.button_accept.grid( row=5, column=0,  padx=2, pady=2, sticky="nsew" )
		self.button_cancel.grid( row=5, column=1,  padx=2, pady=2, sticky="nsew" )

	def AcceptButton( self ):
		pass

	def CancelButton( self ):
		pass






