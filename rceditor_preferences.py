# coding=UTF-8

import tkinter as tk
from tkinter import ttk		# Textbox
from PIL import ImageTk, Image		# Pillow
from tkinter import filedialog
import logging
import sys

import rceditor_lang


def do_nothing():
	x = 0


class Preferences():
	GamePath = None			# String
	SnapTo_Threshold = None		# Integer
	RotBG_Color = None		# Real
	RotBG_Contrast = None		# Real
	RotBG_Brightness = None		# Real
	Language = None			# String (23/7/2021)
	
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
			elif line.find("SnapTo_Threshold") != -1:
				self.SnapTo_Threshold = int( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado SnapTo_Threshold = " + str( self.SnapTo_Threshold ) )
			elif line.find("RotBG_Color") != -1:
				self.RotBG_Color = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado RotBG_Color = " + str( self.RotBG_Color ) )
			elif line.find("RotBG_Contrast") != -1:
				self.RotBG_Contrast = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado RotBG_Contrast = " + str( self.RotBG_Contrast ) )
			elif line.find("RotBG_Brightness") != -1:
				self.RotBG_Brightness = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado RotBG_Brightness = " + str( self.RotBG_Brightness ) )
			elif line.find("Language") != -1:	# (23/7/2021)
				self.Language = line.split("=",1)[1].strip()
				logging.debug( "Encontrado Language = " + self.GamePath )
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
		file1.write( "SnapTo_Threshold=" + self.SnapTo_Threshold )
		file1.write( "RotBG_Color=" + self.RotBG_Color )
		file1.write( "RotBG_Contrast=" + self.RotBG_Contrast )
		file1.write( "RotBG_Brightness=" + self.RotBG_Brightness )
		file1.write( "Language=" + self.Language )		# (23/7/2021)
		####################################################
		# Add new options at this point
		####################################################
		file1.close()


	def SavePreferences_UpdateExisting( self ):
		GamePath_Written = False
		SnapTo_Threshold_Written = False
		RotBG_Color_Written = False
		RotBG_Contrast_Written = False
		RotBG_Brightness_Written = False
		Language_Written = False
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
			elif line.find("SnapTo_Threshold") != -1:
				if SnapTo_Threshold_Written == False:
					file1.write( "SnapTo_Threshold=" + str(self.SnapTo_Threshold) + right_side_remark + "\n")
					SnapTo_Threshold_Written = True
			elif line.find("RotBG_Color") != -1:
				if RotBG_Color_Written == False:
					file1.write( "RotBG_Color=" + str(self.RotBG_Color) + right_side_remark + "\n")
					RotBG_Color_Written = True
			elif line.find("RotBG_Contrast") != -1:
				if RotBG_Contrast_Written == False:
					file1.write( "RotBG_Contrast=" + str(self.RotBG_Contrast) + right_side_remark + "\n")
					RotBG_Contrast_Written = True
			elif line.find("RotBG_Brightness") != -1:
				if RotBG_Brightness_Written == False:
					file1.write( "RotBG_Brightness=" + str(self.RotBG_Brightness) + right_side_remark + "\n")
					RotBG_Brightness_Written = True
			elif line.find("Language") != -1:		# (23/7/2021)
				if Language_Written == False:
					file1.write( "Language=" + str(self.Language) + right_side_remark + "\n")
					Language_Written = True
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
		if SnapTo_Threshold_Written == False:
			file1.write( "SnapTo_Threshold=" + str(self.SnapTo_Threshold) )
			SnapTo_Threshold_Written = True
		if RotBG_Color_Written == False:
			file1.write( "RotBG_Color=" + str(self.RotBG_Color) )
			RotBG_Color_Written == True
		if RotBG_Contrast_Written == False:
			file1.write( "RotBG_Contrast=" + str(self.RotBG_Contrast) )
			RotBG_Contrast_Written = True
		if RotBG_Brightness_Written == False:
			file1.write( "RotBG_Brightness=" + str(self.RotBG_Brightness)  )
			RotBG_Brightness_Written = True
		if Language_Written == False:		# (23/7/2021)
			file1.write( "Language=" + self.Language )
			RotBG_Brightness_Written = True
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
		self.PrefWindow.resizable( False, False )	# Not resizable
		self.PrefWindow.title( _("Preferencias...") )

		self.Load_UI_Icons()

		self.frame_preferences = tk.Frame( master=self.PrefWindow )
		self.label_game_path = tk.Label(master=self.frame_preferences,text= _("Ruta del juego:") )
		self.textbox_game_path = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_game_path.insert(0, preferences.GamePath)
		self.button_choose_game_path = tk.Button(master=self.frame_preferences, width=6, image = self.img_folder_icon, command = self.ChooseGamePathButton )

		self.label_SnapTo_Threshold = tk.Label(master=self.frame_preferences,text= _("Umbral para alin. auto.:") )
		self.textbox_SnapTo_Threshold = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_SnapTo_Threshold.insert(0, str(preferences.SnapTo_Threshold))

		self.label_RotBG_Color = tk.Label(master=self.frame_preferences,text= "RotBG Color:")
		self.textbox_RotBG_Color = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_RotBG_Color.insert(0, str(preferences.RotBG_Color))
		self.label_RotBG_Contrast = tk.Label(master=self.frame_preferences,text="RotBG Contrast:")
		self.textbox_RotBG_Contrast = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_RotBG_Contrast.insert(0, str(preferences.RotBG_Contrast))
		self.label_RotBG_Brightness = tk.Label(master=self.frame_preferences,text="RotBG Brightness:")
		self.textbox_RotBG_Brightness = ttk.Entry(master=self.frame_preferences, width = 15 )
		self.textbox_RotBG_Brightness.insert(0, str(preferences.RotBG_Brightness))

		self.label_language = tk.Label(master=self.frame_preferences,text= _("Idioma:") )	# (23/7/2021)
		self.optionmenu_language_variable = tk.StringVar()
		self.optionmenu_language = tk.OptionMenu( self.frame_preferences, self.optionmenu_language_variable, *rceditor_lang.supported_languages, command=self.Warn_Restart_Required_OptionMenu )
		self.optionmenu_language_variable.set( self.preferences_ref.Language )



		self.frame_preferences.columnconfigure( 0, weight=0, minsize=200)
		self.frame_preferences.columnconfigure( 1, weight=1, minsize=200)
		self.frame_preferences.columnconfigure( 2, weight=1, minsize=100)
		self.frame_preferences.rowconfigure( list(range(6)) , weight=0, minsize=10)

		self.label_game_path.grid( row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.textbox_game_path.grid( row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.button_choose_game_path.grid( row=0, column=2,  padx=2, pady=2, sticky="nsew" )

		self.label_SnapTo_Threshold.grid( row=1, column=0, padx=2, pady=2, sticky="nsew" )
		self.textbox_SnapTo_Threshold.grid( row=1, column=1,  padx=2, pady=2, sticky="nsew" )

		self.label_RotBG_Color.grid( row=2, column=0, padx=2, pady=2, sticky="nsew" )
		self.textbox_RotBG_Color.grid( row=2, column=1,  padx=2, pady=2, sticky="nsew" )
		
		self.label_RotBG_Contrast.grid( row=3, column=0, padx=2, pady=2, sticky="nsew" )
		self.textbox_RotBG_Contrast.grid( row=3, column=1,  padx=2, pady=2, sticky="nsew" )

		self.label_RotBG_Brightness.grid( row=4, column=0, padx=2, pady=2, sticky="nsew" )
		self.textbox_RotBG_Brightness.grid( row=4, column=1,  padx=2, pady=2, sticky="nsew" )

		self.label_language.grid( row=5, column=0, padx=2, pady=2, sticky="nsew" )		# (23/7/2021)
		self.optionmenu_language.grid( row=5, column=1,  padx=2, pady=2, sticky="nsew" )


		self.frame_accept_cancel = tk.Frame( master=self.PrefWindow )
		self.button_accept = tk.Button(master=self.frame_accept_cancel, text= _("Aceptar") , image = self.img_green_tick_icon, compound = tk.LEFT, command = self.AcceptButton )
		self.button_cancel = tk.Button(master=self.frame_accept_cancel, text= _("Cancelar") , image = self.img_red_x_icon, compound = tk.LEFT, command = self.CancelButton )

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
		self.preferences_ref.SnapTo_Threshold = int( self.textbox_SnapTo_Threshold.get() )
		self.preferences_ref.RotBG_Color = float( self.textbox_RotBG_Color.get() ) 
		self.preferences_ref.RotBG_Contrast = float(  self.textbox_RotBG_Contrast.get() )
		self.preferences_ref.RotBG_Brightness = float(  self.textbox_RotBG_Brightness.get() )
		self.preferences_ref.Language = self.optionmenu_language_variable.get()		# (23/7/2021)


	def AcceptButton( self ):
		try:
			self.UpdatePreferences()
		except Exception as e:
			logging.exception(e)
			tk.messagebox.showerror(title= _("Error"), message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
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



	def Warn_Restart_Required_OptionMenu( self, ChosenOption ):
		tk.messagebox.showwarning(title= _("Aviso") , message= _("Este cambio no será efectivo hasta el siguiente reinicio del programa.") )


