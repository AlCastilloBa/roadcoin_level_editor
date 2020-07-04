

import tkinter as tk
from tkinter import ttk		# Textbox
from PIL import ImageTk, Image		# Pillow
from tkinter import filedialog
import logging


def do_nothing():
	x = 0


class Preferences():
	GamePath = None
	
	def LoadPreferences( self ):
		logging.debug( "Leyendo fichero settings" )
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




	def SavePreferences_OverwriteAll( self ):
		logging.debug( "Escribiendo fichero settings (version sobreescribe todo)" )
		file1 = open( "./settings" , 'w' )
		file1.write( "GamePath=" + self.GamePath )
		####################################################
		# Add new options at this point
		####################################################
		file1.close()


	def SavePreferences_UpdateExisting( self ):
		GamePath_Written = False
		####################################################
		# Add new options at this point
		####################################################

		logging.debug( "Escribiendo fichero settings (version actualiza lo existente)" )
		file1 = open( "./settings" , 'r' )
		Lines = file1.readlines()
		file1.close()
		file1 = open( "./settings" , 'w' )
		for idx, line in enumerate(Lines):
			# Strip newline and spaces
			line = line.strip()
			logging.debug( "Actualizando linea "+ str(idx) + ": " + line )
			# Find and save remarks at the right side of " #"
			if line.find(" #") != -1:
				right_side_remark = " #" + line.split(" #",1)[1]
				line = line.split(" #",1)[0]
			else:
				right_side_remark = ""
			# Check if line is empty
			if line == "":
				logging.debug( "Linea vacia")
				file1.write( line + right_side_remark + "\n" )
			# Check if first character is "#" --> This is a remark
			elif line[0] == '#':
				logging.debug( "Esto es un comentario")
				file1.write( line + right_side_remark + "\n")
			elif len(line) == 0:
				logging.debug( "Empty line.")
				file1.write( line + right_side_remark + "\n")
			elif line.find("GamePath") != -1:
				if GamePath_Written == False:
					file1.write( "GamePath=" + self.GamePath + right_side_remark + "\n")
					GamePath_Written = True
			####################################################
			# Add new options at this point
			####################################################
			else:
				logging.debug( "Expresion no reconocida, se ignora" )
				file1.write( line + right_side_remark + "\n")

		# Add not yet written variables at the end of the file
		if GamePath_Written == False:
			file1.write( "GamePath=" + self.GamePath )
			GamePath_Written = True
		####################################################
		# Add new options at this point
		####################################################
		file1.close()				


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

		self.Load_UI_Icons()

		self.frame_preferences = tk.Frame( master=self.PrefWindow )
		self.label_game_path = tk.Label(master=self.frame_preferences,text="Ruta del juego:")
		self.textbox_game_path = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_game_path.insert(0, preferences.GamePath)
		self.button_choose_game_path = tk.Button(master=self.frame_preferences, width=6, image = self.img_folder_icon, command = self.ChooseGamePathButton )

		self.frame_preferences.columnconfigure( 0, weight=0, minsize=200)
		self.frame_preferences.columnconfigure( 1, weight=1, minsize=200)
		self.frame_preferences.columnconfigure( 2, weight=1, minsize=100)
		self.frame_preferences.rowconfigure( list(range(5)) , weight=0, minsize=10)

		self.label_game_path.grid( row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.textbox_game_path.grid( row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.button_choose_game_path.grid( row=0, column=2,  padx=2, pady=2, sticky="nsew" )


		self.frame_accept_cancel = tk.Frame( master=self.PrefWindow )
		self.button_accept = tk.Button(master=self.frame_accept_cancel, text="Aceptar", image = self.img_green_tick_icon, compound = tk.LEFT, command = self.AcceptButton )
		self.button_cancel = tk.Button(master=self.frame_accept_cancel, text="Cancelar", image = self.img_red_x_icon, compound = tk.LEFT, command = self.CancelButton )

		self.button_accept.grid( row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.button_cancel.grid( row=0, column=1,  padx=2, pady=2, sticky="nsew" )

		self.frame_accept_cancel.columnconfigure( [0, 1], weight=1)
		self.frame_accept_cancel.rowconfigure( 0, weight=1 )


		self.frame_preferences.pack( side=tk.TOP, padx=2, pady=2 )
		self.frame_accept_cancel.pack( side=tk.TOP, padx=2, pady=2 )




	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de propiedades" )
		self.img_folder_icon = ImageTk.PhotoImage(Image.open("icons/open_folder-16.png"))   # PIL solution
		self.img_green_tick_icon = ImageTk.PhotoImage(Image.open("icons/green_tick-16.png"))
		self.img_red_x_icon = ImageTk.PhotoImage(Image.open("icons/red_x_icon-16.png"))

	def UpdatePreferences( self ):
		logging.debug( "Aplicando cambios en las propiedades" )
		self.preferences_ref.GamePath = self.textbox_game_path.get()


	def AcceptButton( self ):
		self.UpdatePreferences()
		#self.preferences_ref.SavePreferences_OverwriteAll()
		self.preferences_ref.SavePreferences_UpdateExisting()
		self.PrefWindow.destroy()

	def CancelButton( self ):
		self.PrefWindow.destroy()

	def ChooseGamePathButton( self ):
		# chosen_new_game_path = filedialog.askopenfilename(initialdir = self.preferences.GamePath, title = "Select file",filetypes = (("all files","*"),("all files with ext","*.*"),("jpeg files","*.jpg")))
		chosen_new_game_path = filedialog.askdirectory( initialdir = self.preferences_ref.GamePath, title = "Select directory" )
		if isinstance( chosen_new_game_path, str ) and (chosen_new_game_path!="") :
			# Note: when <type 'str'> # File selected, OK clicked
			self.textbox_game_path.delete(0, 'end')
			self.textbox_game_path.insert(0, chosen_new_game_path)
		#elif isinstance( chosen_new_game_path, unicode ):
			# Note: when<type 'unicode'> # Nothing selected, Cancel clicked
		#elif isinstance( chosen_new_game_path, tuple ):
			# Note: when <type 'tuple'> # File selected, Cancel clicked
			# Note: when <type 'tuple'> # Multiple files selected, OK clicked






