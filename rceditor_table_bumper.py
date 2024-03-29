# coding=UTF-8

import tkinter as tk
from tkinter import ttk		# Textbox
from PIL import ImageTk, Image		# Pillow
# from tkinter import filedialog
from tkinter import messagebox
import logging
import sys


import scrframe

import rceditor_maps
import rceditor_user_interface

import rceditor_lang


def do_nothing():
	x = 0

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False



class Bumper_Table_Window():
	map_ref = None		# Reference to map object
	owner_ref = None		# Reference to owner caller object (the application's main user interface that calls this windows)
	bumper_number_handler_dict = dict()
	center_x_handler_dict = dict()
	center_y_handler_dict = dict()
	radius_handler_dict = dict()
	speed_handler_dict = dict()

	selected_row_number = None


	def __init__( self, master , Map, owner ):
		self.map_ref = Map
		self.owner_ref = owner

		self.BumperTableWindow = tk.Toplevel( master )
		self.BumperTableWindow.transient( master )		# Make this window be child of parent
		# self.BumperTableWindow.grab_set()			# Make this window Modal
		# self.BumperTableWindow.protocol('WM_DELETE_WINDOW',do_nothing)		# Close window button behaviour
		# self.PrefWindow.attributes('-topmost', 'true')		# Stay on top of all others
		self.BumperTableWindow.title( _("Tabla de bumpers") )
		self.BumperTableWindow.protocol("WM_DELETE_WINDOW", self.window_close_button_handler)

		self.Load_UI_Icons()

		self.frame_upper_buttons = tk.Frame( master=self.BumperTableWindow )
		self.button_new_row = tk.Button(master=self.frame_upper_buttons, text= _("Nueva fila") , image = self.img_new_row_icon, compound = tk.LEFT, command = self.New_Row_At_End_Of_Table )
		self.button_new_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		self.button_delete_row = tk.Button(master=self.frame_upper_buttons, text= _("Eliminar fila") , image = self.img_delete_row_icon, compound = tk.LEFT, command = self.Delete_Selected_Bumper )
		self.button_delete_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		# self.button_update_canvas = tk.Button(master=self.frame_upper_buttons, text="Actualizar mapa editor (desde tabla)", image = self.img_update_icon, compound = tk.LEFT, command = do_nothing )
		# self.button_update_canvas.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
		self.button_update_table = tk.Button(master=self.frame_upper_buttons, text= _("Actualizar tabla (desde mapa editor)") , image = self.img_update_icon, compound = tk.LEFT, command = self.update_table_from_map_editor )
		self.button_update_table.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
		self.frame_upper_buttons.pack( side=tk.TOP, fill=tk.BOTH, expand=False )

		logging.debug( "Tabla de bumpers, creando primera fila (leyenda)" )
		self.frame_upper_first_row = tk.Frame( master=self.BumperTableWindow )
		self.frame_upper_first_row.columnconfigure( [0, 1, 2, 3, 4], weight=1)
		self.frame_upper_first_row.columnconfigure( 5, weight=0)		# Scrollbar gap does not grow with window resizing
		self.frame_upper_first_row.rowconfigure( 0, weight=0 )
		self.first_row_bumper_number = tk.Button( master=self.frame_upper_first_row, text= _("Num bump") , command = do_nothing, width = 3 )
		self.first_row_bumper_number.grid( row=0, column=0,  padx=0, pady=0, sticky="nsew" )
		self.first_row_center_x = tk.Button( master=self.frame_upper_first_row, text="Center X", command = do_nothing, width = 15 )
		self.first_row_center_x.grid( row=0, column=1,  padx=0, pady=0, sticky="nsew" )
		self.first_row_center_y = tk.Button( master=self.frame_upper_first_row, text="Center Y", command = do_nothing , width = 15)
		self.first_row_center_y.grid( row=0, column=2,  padx=0, pady=0, sticky="nsew" )
		self.first_row_radius = tk.Button( master=self.frame_upper_first_row, text="Radius", command = do_nothing, width = 15 )
		self.first_row_radius.grid( row=0, column=3,  padx=0, pady=0, sticky="nsew" )
		self.first_row_speed = tk.Button( master=self.frame_upper_first_row, text="Speed", command = do_nothing, width = 15 )
		self.first_row_speed.grid( row=0, column=4,  padx=0, pady=0, sticky="nsew" )
	
		# self.first_row_scrollbar_gap = tk.Button( master=self.frame_upper_first_row, text="", command = do_nothing, width = 0.3 )
		self.first_row_scrollbar_gap = tk.Scrollbar(master=self.frame_upper_first_row, orient=tk.VERTICAL)
		self.first_row_scrollbar_gap.grid( row=0, column=7,  padx=0, pady=0, sticky="nsew" )

		# FALTAN FILAS
		self.frame_upper_first_row.pack( side=tk.TOP, fill=tk.BOTH, expand=False )


		self.frame_table_frame = scrframe.VerticalScrolledFrame( master=self.BumperTableWindow )
		self.frame_table_frame.pack( side=tk.TOP, fill=tk.BOTH, expand=True )
		self.frame_table_frame.interior.columnconfigure( [0, 1, 2, 3, 4], weight=1)	# Esto es asi o es en interior ??????????????

		# Create the table elements
		self.update_table_from_map_editor()



	def __del__( self ):
		logging.debug( "Eliminando objeto Bumper_Table_Window" )
		self.delete_table_widgets()
		self.bumper_number_handler_dict.clear()
		self.center_x_handler_dict.clear()
		self.center_y_handler_dict.clear()
		self.radius_handler_dict.clear()
		self.speed_handler_dict.clear()
		self.BumperTableWindow.destroy()
		self.map_ref = None
		self.owner_ref = None


	def window_close_button_handler( self ):
		logging.debug( "Ejecutando window_close_button_handler" )
		# self.BumperTableWindow.destroy()
		self.map_ref = None
		self.owner_ref.bumper_table = None
		self.owner_ref = None
		self.__del__()
		del self
		# self = None



	def delete_table_widgets( self ):
		# This function deletes all created widgets on the VerticalScrolledFrame
		logging.debug( "Tabla de bumpers, borrando widgets y vaciando diccionarios" )

		# Bumper number
		for row, bumper_num_ref in self.bumper_number_handler_dict.items():
			# bumper_num_ref.grid_forget()
			bumper_num_ref.destroy()
		self.bumper_number_handler_dict.clear()

		# Center X
		for row, center_x_ref in self.center_x_handler_dict.items():
			# center_x_ref.grid_forget()
			center_x_ref.destroy()
		self.center_x_handler_dict.clear()

		# Center Y
		for row, center_y_ref in self.center_y_handler_dict.items():
			# center_y_ref.grid_forget()
			center_y_ref.destroy()
		self.center_y_handler_dict.clear()

		# Radius
		for row, radius_ref in self.radius_handler_dict.items():
			# radius_ref.grid_forget()
			radius_ref.destroy()
		self.radius_handler_dict.clear()

		# Speed
		for row, speed_ref in self.speed_handler_dict.items():
			# speed_ref.grid_forget()
			speed_ref.destroy()
		self.speed_handler_dict.clear()



	def update_table_from_map_editor( self ):
		# This function updates table contents from map data to the table
		self.delete_table_widgets()
		# Create the table elements
		for row in range(0, self.map_ref.pinball_bumpers_number):
			logging.debug( "Tabla de bumpers, añadiendo fila " + str( row ) )
		
			self.frame_table_frame.interior.rowconfigure( row, weight=1 )	# Esto es asi o es en interior ??????????????
			# Bumper number
			bumper_num_ref = tk.Label( master = self.frame_table_frame.interior, text=str( row ), width = 3 )
			self.bumper_number_handler_dict.setdefault( row , bumper_num_ref )
			bumper_num_ref.grid( row=row, column=0,  padx=0, pady=0, sticky="nsew" )

			# Center X
			center_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			center_x_ref.insert(0, self.map_ref.pinball_bumpers_dict.get( row ).center.x )
			self.center_x_handler_dict.setdefault( row , center_x_ref )
			center_x_ref.grid( row=row, column=1,  padx=0, pady=0, sticky="nsew" )
			center_x_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			center_x_ref.bind( "<FocusOut>", self.Bumper_Table_RealNumber_FocusOut_Callback )
			self.orig_font = center_x_ref.cget("font")	# Get original font in order to restore later

			# Center Y
			center_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			center_y_ref.insert(0, self.map_ref.pinball_bumpers_dict.get( row ).center.y )
			self.center_y_handler_dict.setdefault( row , center_y_ref )
			center_y_ref.grid( row=row, column=2,  padx=0, pady=0, sticky="nsew" )
			center_y_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			center_y_ref.bind( "<FocusOut>", self.Bumper_Table_RealNumber_FocusOut_Callback )

			# Radius
			radius_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			radius_ref.insert(0, self.map_ref.pinball_bumpers_dict.get( row ).radius )
			self.radius_handler_dict.setdefault( row , radius_ref )
			radius_ref.grid( row=row, column=3,  padx=0, pady=0, sticky="nsew" )
			radius_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			radius_ref.bind( "<FocusOut>", self.Bumper_Table_RealNumber_FocusOut_Callback )

			# Speed
			speed_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			speed_ref.insert(0, self.map_ref.pinball_bumpers_dict.get( row ).exit_speed )
			self.speed_handler_dict.setdefault( row , speed_ref )
			speed_ref.grid( row=row, column=4,  padx=0, pady=0, sticky="nsew" )
			speed_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			speed_ref.bind( "<FocusOut>", self.Bumper_Table_RealNumber_FocusOut_Callback )


	def update_table_row_values_from_map( self, row_number ):
		# This function writes values again on a row, from the map data

		# Center X
		self.center_x_handler_dict.get( row_number ).delete(0,tk.END)
		self.center_x_handler_dict.get( row_number ).insert(0, self.map_ref.pinball_bumpers_dict.get( row_number ).center.x )
		# Center Y
		self.center_y_handler_dict.get( row_number ).delete(0,tk.END)
		self.center_y_handler_dict.get( row_number ).insert(0, self.map_ref.pinball_bumpers_dict.get( row_number ).center.y )
		# Radius
		self.radius_handler_dict.get( row_number ).delete(0,tk.END)
		self.radius_handler_dict.get( row_number ).insert(0, self.map_ref.pinball_bumpers_dict.get( row_number ).radius )
		# Speed
		self.speed_handler_dict.get( row_number ).delete(0,tk.END)
		self.speed_handler_dict.get( row_number ).insert(0, self.map_ref.pinball_bumpers_dict.get( row_number ).exit_speed )


	def update_map_editor_from_table( self ):
		# This function updates map data and forces a full map redraw
		pass


	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de tabla de bumper" )
		self.img_new_row_icon = ImageTk.PhotoImage(Image.open("icons/new_row_end-16.png"))   # PIL solution
		self.img_delete_row_icon = ImageTk.PhotoImage(Image.open("icons/delete_row-16.png"))
		self.img_update_icon = ImageTk.PhotoImage(Image.open("icons/reload-16.png"))


	def Focus_In_Callback( self, event ):
		if (self.owner_ref.current_mode == rceditor_user_interface.Mode.bumper) and (self.owner_ref.current_bumper_submode == rceditor_user_interface.Bumper_SubMode.edit):
			# This callback function will be executed every time a widget has been selected (focus-in)
			# (if everything has been setup correctly)
			selected_widget_handler = event.widget
			logging.debug( "FocusIn: El foco está en el widget " + str( selected_widget_handler ) )
			# Get selected row number
			self.selected_row_number = self.Get_Selected_Row_Number( selected_widget_handler )
			logging.debug( "FocusIn: El foco está en la fila " + str( self.selected_row_number ) )
			if self.selected_row_number is None:
				logging.debug( "FocusIn: Error de programacion: no se puede determinar la fila de la tabla a la que pertenece el widget." )
				return
			# UnHiglight all rows
			self.UnHighlight_All_Rows()
			# Highlight row
			self.Highlight_Row( self.selected_row_number )
		else:
			logging.debug( "FocusIn: Se ha llamado a la funcion Focus_In_Callback en el modo incorrecto." )
			# We focus on another object (to prevent to focus in again and keep calling this function forever)
			self.frame_upper_buttons.focus()
			tk.messagebox.showinfo(title= _("Aviso") , message= _("Para editar, seleccionar modo bumpers y modo editar.") )
			self.UnHighlight_All_Rows()
			self.selected_row_number = None


	def Get_Selected_Row_Number(self, selected_widget_handler ):
		for row,handler in self.center_x_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.center_y_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.radius_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.speed_handler_dict.items():
			if handler == selected_widget_handler:
				return row		
		# No widget handler matches the selected widget handler
		return None




	def Highlight_Row( self, row_number ):
		self.center_x_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red") # , font="Bold" )
		self.center_y_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red") # , font="Bold" )
		self.radius_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red") # , font="Bold" )
		self.speed_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red") # , font="Bold" )
		# Select bumper in the main window editor
		self.owner_ref.canvas_mapview.UnHighlight_All()
		self.owner_ref.canvas_mapview.Highlight_Bumpers( [row_number] )
		self.owner_ref.Update_Selected_Bumper_Properties( row_number )


	def UnHighlight_All_Rows( self ):
		for row,handler in self.center_x_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.center_y_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.radius_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.speed_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )



	def Apply_Selected_Row_Changes( self, selected_row ):
		# When a bumper is selected on the table, and some values are changed in the properties frame, this function applies the changes to the "bumper dictionary"
		# Only to be taken into account in the bumper edit mode
		if self.owner_ref.current_mode == rceditor_user_interface.Mode.bumper and self.owner_ref.current_bumper_submode == rceditor_user_interface.Bumper_SubMode.edit:
			logging.debug( "Funcion Apply_Selected_Row_Changes llamada, para la fila " + str(selected_row) + ", + se intentan aplicar los cambios al diccionario." )
			try:
				# Read selected bumper
				bumper_number = selected_row
				# Get bumper center coordinates
				self.map_ref.pinball_bumpers_dict.get(bumper_number).center.x = float( self.center_x_handler_dict.get( bumper_number ).get() )
				self.map_ref.pinball_bumpers_dict.get(bumper_number).center.y = float( self.center_y_handler_dict.get( bumper_number ).get() )
				# Get radius
				self.map_ref.pinball_bumpers_dict.get(bumper_number).radius = float( self.radius_handler_dict.get( bumper_number ).get() )
				# Get speed
				self.map_ref.pinball_bumpers_dict.get(bumper_number).speed = float( self.speed_handler_dict.get( bumper_number ).get() )

				# Update canvas display on main window editor
				self.owner_ref.canvas_mapview.Update_Bumpers_Display( [bumper_number], self.map_ref )
				self.owner_ref.canvas_mapview.Highlight_Bumpers( [bumper_number] )		# Type cast into list. After update, we need to highlight again
				self.owner_ref.Update_Selected_Bumper_Properties( bumper_number )
				# Update table contents again (to check program consistency)
				self.update_table_row_values_from_map( selected_row )

				logging.debug( "Modificaciones bumper leidas desde tabla: bumper_num = " + str(bumper_number) + \
						", center: x= " + str(self.map_ref.pinball_bumpers_dict.get(bumper_number).center.x) + \
						", y= " + str( self.map_ref.pinball_bumpers_dict.get(bumper_number).center.y ) + \
						", radius= " + str(self.map_ref.pinball_bumpers_dict.get(bumper_number).radius) + \
						", speed= " + str( self.map_ref.pinball_bumpers_dict.get(bumper_number).speed)  )
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Selected_Row_Changes llamada, pero en el modo incorrecto. No se hace nada." )



	def Bumper_Table_RealNumber_FocusOut_Callback( self, event ):
		# This is the callback function called everytime an entry widget loses focus
		selected_widget_handler = event.widget
		logging.debug( "Llamada a función Bumper_Table_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) + \
				", widget_name = " + str(selected_widget_handler) )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.bumper:
				# Get selected row number
				self.selected_row_number = self.Get_Selected_Row_Number( selected_widget_handler )
				logging.debug( "FocusOut: El foco va a dejar de estar en la fila " + str( self.selected_row_number ) )
				if self.selected_row_number is None:
					logging.debug( "FocusOut: Error de programacion: no se puede determinar la fila de la tabla a la que pertenece el widget." )
					return
				
				text_after_change = selected_widget_handler.get()

				if isFloat(text_after_change) == True:
					logging.debug("FocusOut: El nuevo texto es un numero.")
					self.Apply_Selected_Row_Changes( self.selected_row_number )
					#return(True)
				else:
					logging.debug("FocusOut: El nuevo texto no es un numero.")
					tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
					#return(False)
			else:
				logging.debug("FocusOut: Modo incorrecto. No se hace nada.")
				#return(False)	
		else:
			logging.debug("FocusOut: Mapa no cargado. No se hace nada")
			#return(False)


	def Bumper_Table_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Bumper_Table_Checkbox_Click_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.bumper:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def Bumper_Table_OptionMenu_Click_Callback( self, ChosenOption ):
		# This function will be called when a OptionMenu on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Bumper_Property_OptionMenu_Click_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) + \
				", opcion elegida: " + ChosenOption )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.bumper:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")



	def Delete_Selected_Bumper( self ):
		# When a bumper is selected and the delete button is pressed, this function makes the actions to delete it.
		if self.owner_ref.map_loaded == True:
			if self.selected_row_number is not None:
				answer = tk.messagebox.askyesnocancel( _("Eliminar bumper") , _("¿Desea eliminar el bumper numero ") + str(self.selected_row_number) + "?")
				logging.debug( "Pregunta eliminar bumper, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected bumper will be deleted
				self.owner_ref.mapa_cargado.DeletePinballBumper( self.selected_row_number )
				self.owner_ref.mapa_cargado.Bumpers_Reenumerate()
				self.owner_ref.canvas_mapview.DrawAll( self.owner_ref.mapa_cargado )
				self.owner_ref.Unselect_All()
				self.owner_ref.window_statusbar.set_field_1("%s %s %s", _("Bumper ") , self.selected_row_number , _(" borrado") )
				# Redraw table
				self.update_table_from_map_editor()
				# No bumper is selected (4/7/2021)
				self.selected_row_number = None
			else:
				tk.messagebox.showerror(title= _("Error") , message= _("Ninguna fila seleccionada.") )
				logging.debug( "En funcion Delete_Bumper, error: ninguna fila seleccionada." )

		else:
			tk.messagebox.showerror(title= _("Error"), message= _("No hay ningún mapa cargado.") )



	def New_Row_At_End_Of_Table( self ):
		# This function creates a new row at the table, and declares this as a new bumper
		if self.owner_ref.map_loaded == True:
			# Before doing anything, we apply the currently selected row changes (or we will lose them) (4/7/2021)
			if self.selected_row_number is not None:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			# Unselect everything
			self.UnHighlight_All_Rows()
			self.selected_row_number = None
			# Declare new bumper data (with default values)
			new_bumper = rceditor_maps.Pinball_Bumper( center=rceditor_maps.Point(x=0,y=0), radius=50, exit_speed=100)
			# Create new bumper
			self.map_ref.AddPinballBumper( new_bumper )
			# Update main window editor canvas
			self.owner_ref.canvas_mapview.DrawSingleBumper( Map=self.map_ref, num_bumper=self.map_ref.pinball_bumpers_number-1 )
			self.owner_ref.canvas_mapview.DrawSingleBumperNumber( Map=self.map_ref, num_bumper=self.map_ref.pinball_bumpers_number-1 )
			# Update table
			self.update_table_from_map_editor()
			# Move canvas to lower position (4/7/2021)
			self.frame_table_frame.ScrollToBottom()





