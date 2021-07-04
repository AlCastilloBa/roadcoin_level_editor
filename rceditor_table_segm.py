
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



def do_nothing():
	x = 0

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class Segment_Table_Window():
	map_ref = None		# Reference to map object
	owner_ref = None		# Reference to owner caller object (the application's main user interface that calls this windows)
	segm_number_handler_dict = dict()
	start_x_handler_dict = dict()
	start_y_handler_dict = dict()
	end_x_handler_dict = dict()
	end_y_handler_dict = dict()
	type_handler_dict = dict()
	type_variable_dict = dict()
	invis_handler_dict = dict()
	invis_variable_dict = dict()

	selected_row_number = None


	def __init__( self, master , Map, owner ):
		self.map_ref = Map
		self.owner_ref = owner

		self.SegmentTableWindow = tk.Toplevel( master )
		self.SegmentTableWindow.transient( master )		# Make this window be child of parent
		# self.SegmentTableWindow.grab_set()			# Make this window Modal
		# self.SegmentTableWindow.protocol('WM_DELETE_WINDOW',do_nothing)		# Close window button behaviour
		# self.PrefWindow.attributes('-topmost', 'true')		# Stay on top of all others
		self.SegmentTableWindow.title("Tabla de segmentos")
		self.SegmentTableWindow.protocol("WM_DELETE_WINDOW", self.window_close_button_handler)

		self.Load_UI_Icons()

		self.frame_upper_buttons = tk.Frame( master=self.SegmentTableWindow )
		self.button_new_row = tk.Button(master=self.frame_upper_buttons, text="Nueva fila", image = self.img_new_row_icon, compound = tk.LEFT, command = self.New_Row_At_End_Of_Table )
		self.button_new_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		self.button_delete_row = tk.Button(master=self.frame_upper_buttons, text="Eliminar fila", image = self.img_delete_row_icon, compound = tk.LEFT, command = self.Delete_Selected_Segment )
		self.button_delete_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		# self.button_update_canvas = tk.Button(master=self.frame_upper_buttons, text="Actualizar mapa editor (desde tabla)", image = self.img_update_icon, compound = tk.LEFT, command = do_nothing )
		# self.button_update_canvas.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
		self.button_update_table = tk.Button(master=self.frame_upper_buttons, text="Actualizar tabla (desde mapa editor)", image = self.img_update_icon, compound = tk.LEFT, command = self.update_table_from_map_editor )
		self.button_update_table.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
		self.frame_upper_buttons.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
		

		logging.debug( "Tabla de segmentos, creando primera fila (leyenda)" )
		self.frame_upper_first_row = tk.Frame( master=self.SegmentTableWindow )
		self.frame_upper_first_row.columnconfigure( [0, 1, 2, 3, 4, 5, 6], weight=1)
		self.frame_upper_first_row.columnconfigure( 7, weight=0)		# Scrollbar gap does not grow with window resizing
		self.frame_upper_first_row.rowconfigure( 0, weight=0 )
		self.first_row_segm_number = tk.Button( master=self.frame_upper_first_row, text="Num segm", command = do_nothing, width = 3 )
		self.first_row_segm_number.grid( row=0, column=0,  padx=0, pady=0, sticky="nsew" )
		self.first_row_start_x = tk.Button( master=self.frame_upper_first_row, text="Start X", command = do_nothing, width = 15 )
		self.first_row_start_x.grid( row=0, column=1,  padx=0, pady=0, sticky="nsew" )
		self.first_row_start_y = tk.Button( master=self.frame_upper_first_row, text="Start Y", command = do_nothing , width = 15)
		self.first_row_start_y.grid( row=0, column=2,  padx=0, pady=0, sticky="nsew" )
		self.first_row_end_x = tk.Button( master=self.frame_upper_first_row, text="End X", command = do_nothing, width = 15 )
		self.first_row_end_x.grid( row=0, column=3,  padx=0, pady=0, sticky="nsew" )
		self.first_row_end_y = tk.Button( master=self.frame_upper_first_row, text="End Y", command = do_nothing, width = 15 )
		self.first_row_end_y.grid( row=0, column=4,  padx=0, pady=0, sticky="nsew" )
		self.first_type = tk.Button( master=self.frame_upper_first_row, text="Tipo", command = do_nothing, width = 15 )
		self.first_type.grid( row=0, column=5,  padx=0, pady=0, sticky="nsew" )
		self.first_invis = tk.Button( master=self.frame_upper_first_row, text="Invisible", command = do_nothing, width = 15 )
		self.first_invis.grid( row=0, column=6,  padx=0, pady=0, sticky="nsew" )
		# self.first_row_scrollbar_gap = tk.Button( master=self.frame_upper_first_row, text="", command = do_nothing, width = 0.3 )
		self.first_row_scrollbar_gap = tk.Scrollbar(master=self.frame_upper_first_row, orient=tk.VERTICAL)
		self.first_row_scrollbar_gap.grid( row=0, column=7,  padx=0, pady=0, sticky="nsew" )

		# FALTAN FILAS
		self.frame_upper_first_row.pack( side=tk.TOP, fill=tk.BOTH, expand=False )


		self.frame_table_frame = scrframe.VerticalScrolledFrame( master=self.SegmentTableWindow )
		self.frame_table_frame.pack( side=tk.TOP, fill=tk.BOTH, expand=True )
		self.frame_table_frame.interior.columnconfigure( [0, 1, 2, 3, 4, 5, 6], weight=1)	# Esto es asi o es en interior ??????????????


		self.segm_type_choices = [ rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.wall), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.goal), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.death), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_L), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_R)  ]
		# Create the table elements
		self.update_table_from_map_editor()



	def __del__( self ):
		logging.debug( "Eliminando objeto Segment_Table_Window" )
		self.delete_table_widgets()
		self.segm_number_handler_dict.clear()
		self.start_x_handler_dict.clear()
		self.start_y_handler_dict.clear()
		self.end_x_handler_dict.clear()
		self.end_y_handler_dict.clear()
		self.type_handler_dict.clear()
		self.type_variable_dict.clear()
		self.invis_handler_dict.clear()
		self.invis_variable_dict.clear()
		self.SegmentTableWindow.destroy()
		self.map_ref = None
		self.owner_ref = None




	def window_close_button_handler( self ):
		logging.debug( "Ejecutando window_close_button_handler" )
		# self.SegmentTableWindow.destroy()
		self.map_ref = None
		self.owner_ref.segment_table = None		# (TODO) PROBAR 16/3/2021
		self.owner_ref = None
		self.__del__()
		del self
		# self = None


	def delete_table_widgets( self ):
		# This function deletes all created widgets on the VerticalScrolledFrame
		logging.debug( "Tabla de segmentos, borrando widgets y vaciando diccionarios" )
			
		# Segment number
		for row, segm_num_ref in self.segm_number_handler_dict.items():
			# segm_num_ref.grid_forget()
			segm_num_ref.destroy()
		self.segm_number_handler_dict.clear()

		# Start X
		for row, start_x_ref in self.start_x_handler_dict.items():
			# start_x_ref.grid_forget()
			start_x_ref.destroy()
		self.start_x_handler_dict.clear()

		# Start Y
		for row, start_y_ref in self.start_y_handler_dict.items():
			# start_y_ref.grid_forget()
			start_y_ref.destroy()
		self.start_y_handler_dict.clear()

		# End X
		for row, end_x_ref in self.end_x_handler_dict.items():
			# end_x_ref.grid_forget()
			end_x_ref.destroy()
		self.end_x_handler_dict.clear()

		# End Y
		for row, end_y_ref in self.end_y_handler_dict.items():
			# end_y_ref.grid_forget()
			end_y_ref.destroy()
		self.end_y_handler_dict.clear()

		# Type
		for row, type_ref in self.type_handler_dict.items():
			# type_ref.grid_forget()
			type_ref.destroy()
		self.type_handler_dict.clear()
		self.type_variable_dict.clear()

		# Invis
		for row, invis_ref in self.invis_handler_dict.items():
			# invis_ref.grid_forget()
			invis_ref.destroy()
		self.invis_handler_dict.clear()
		self.invis_variable_dict.clear()



	def update_table_from_map_editor( self ):
		#### Register validation methods
		##Segment_RealNumber_Validation = self.SegmentTableWindow.register(  self.Segment_Table_RealNumber_Change_FocusOut_Validation_Callback  )

		# This function updates table contents from map data to the table
		self.delete_table_widgets()
		# Create the table elements
		for row in range(0, self.map_ref.segment_number):
			logging.debug( "Tabla de segmentos, añadiendo fila " + str( row ) )
			
			self.frame_table_frame.interior.rowconfigure( row, weight=1 )	# Esto es asi o es en interior ??????????????
			# Segment number
			segm_num_ref = tk.Label( master = self.frame_table_frame.interior, text=str( row ), width = 3 )
			self.segm_number_handler_dict.setdefault( row , segm_num_ref )
			segm_num_ref.grid( row=row, column=0,  padx=0, pady=0, sticky="nsew" )
			# Start X
			start_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			start_x_ref.insert(0, self.map_ref.segment_dict.get( row ).start.x )
			self.start_x_handler_dict.setdefault( row , start_x_ref )
			start_x_ref.grid( row=row, column=1,  padx=0, pady=0, sticky="nsew" )
			start_x_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			start_x_ref.bind( "<FocusOut>", self.Segment_Table_RealNumber_FocusOut_Callback )
			self.orig_font = start_x_ref.cget("font")	# Get original font in order to restore later
			# Start Y
			start_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			start_y_ref.insert(0, self.map_ref.segment_dict.get( row ).start.y )
			self.start_y_handler_dict.setdefault( row , start_y_ref )
			start_y_ref.grid( row=row, column=2,  padx=0, pady=0, sticky="nsew" )
			start_y_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			start_y_ref.bind( "<FocusOut>", self.Segment_Table_RealNumber_FocusOut_Callback )
			# End X
			end_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			end_x_ref.insert(0, self.map_ref.segment_dict.get( row ).end.x )
			self.end_x_handler_dict.setdefault( row , end_x_ref )
			end_x_ref.grid( row=row, column=3,  padx=0, pady=0, sticky="nsew" )
			end_x_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			end_x_ref.bind( "<FocusOut>", self.Segment_Table_RealNumber_FocusOut_Callback )
			# End Y
			end_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			end_y_ref.insert(0, self.map_ref.segment_dict.get( row ).end.y )
			self.end_y_handler_dict.setdefault( row , end_y_ref )		
			end_y_ref.grid( row=row, column=4,  padx=0, pady=0, sticky="nsew" )	
			end_y_ref.bind( "<FocusIn>", self.Focus_In_Callback )
			end_y_ref.bind( "<FocusOut>", self.Segment_Table_RealNumber_FocusOut_Callback )
			# Type
			type_variable = tk.StringVar()
			type_ref = tk.OptionMenu( self.frame_table_frame.interior, type_variable, *self.segm_type_choices, command=self.Segment_Table_OptionMenu_Click_Callback )
			type_variable.set( self.segm_type_choices[ self.map_ref.segment_dict.get(row).segm_type ] )
			type_ref.configure( width = 12 )
			self.type_handler_dict.setdefault( row , type_ref )
			self.type_variable_dict.setdefault( row , type_variable )
			type_ref.grid( row=row, column=5,  padx=0, pady=0, sticky="nsew" )
			type_ref.bind( "<Button-1>", self.Focus_In_Callback )
			# Invis
			invis_variable = tk.BooleanVar()
			invis_ref = tk.Checkbutton(master=self.frame_table_frame.interior, text="Invisible", var=invis_variable, width = 12, command = self.Segment_Table_Checkbox_Click_Callback )
			if self.map_ref.segment_dict.get(row).invisible == True:
				invis_ref.select()
			else:
				invis_ref.deselect()
			self.invis_handler_dict.setdefault( row , invis_ref )
			self.invis_variable_dict.setdefault( row , invis_variable )
			invis_ref.grid( row=row, column=6,  padx=0, pady=0, sticky="nsew" )
			invis_ref.bind( "<Button-1>", self.Focus_In_Callback )



	def update_table_row_values_from_map( self, row_number ):
		# This function writes values again on a row, from the map data
		# Start X
		self.start_x_handler_dict.get( row_number ).delete(0,tk.END)
		self.start_x_handler_dict.get( row_number ).insert(0, self.map_ref.segment_dict.get( row_number ).start.x )
		# Start Y
		self.start_y_handler_dict.get( row_number ).delete(0,tk.END)
		self.start_y_handler_dict.get( row_number ).insert(0, self.map_ref.segment_dict.get( row_number ).start.y )
		# End X
		self.end_x_handler_dict.get( row_number ).delete(0,tk.END)
		self.end_x_handler_dict.get( row_number ).insert(0, self.map_ref.segment_dict.get( row_number ).end.x )
		# End Y
		self.end_y_handler_dict.get( row_number ).delete(0,tk.END)
		self.end_y_handler_dict.get( row_number ).insert(0, self.map_ref.segment_dict.get( row_number ).end.y )
		# Type
		self.type_variable_dict.get( row_number ).set( self.segm_type_choices[ self.map_ref.segment_dict.get( row_number ).segm_type ] )
		# Invis
		if self.map_ref.segment_dict.get( row_number ).invisible == True:
			self.invis_handler_dict.get( row_number ).select()
		else:
			self.invis_handler_dict.get( row_number ).deselect()


	def update_map_editor_from_table( self ):
		# This function updates map data and forces a full map redraw
		pass




	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de tabla de segmentos" )
		self.img_new_row_icon = ImageTk.PhotoImage(Image.open("icons/new_row_end-16.png"))   # PIL solution
		self.img_delete_row_icon = ImageTk.PhotoImage(Image.open("icons/delete_row-16.png"))
		self.img_update_icon = ImageTk.PhotoImage(Image.open("icons/reload-16.png"))


	def Focus_In_Callback( self, event ):
		if (self.owner_ref.current_mode == rceditor_user_interface.Mode.segment) and (self.owner_ref.current_segment_submode == rceditor_user_interface.Segment_SubMode.edit):
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
			tk.messagebox.showinfo(title="Aviso", message="Para editar, seleccionar modo segmentos y modo editar.")
			self.UnHighlight_All_Rows()
			self.selected_row_number = None


	def Get_Selected_Row_Number(self, selected_widget_handler ):
		for row,handler in self.start_x_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.start_y_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.end_x_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.end_y_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.type_handler_dict.items():
			if handler == selected_widget_handler:
				return row
		for row,handler in self.invis_handler_dict.items():
			if handler == selected_widget_handler:
				return row		
		# No widget handler matches the selected widget handler
		return None

	def Highlight_Row( self, row_number ):
		self.start_x_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red" ) #  [ , font="Bold" ]
		self.start_y_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red" ) #  [ , font="Bold" ]
		self.end_x_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red" ) #  [ , font="Bold" ]
		self.end_y_handler_dict.get( row_number ).configure( background = "yellow", foreground = "red" ) #  [, font="Bold" ]
		self.type_handler_dict.get( row_number ).configure( foreground = "red" ) #  [, font="Bold" ]
		self.invis_handler_dict.get( row_number ).configure( foreground = "red" ) #  [, font="Bold" ]
		# Select segment in the main window editor
		self.owner_ref.canvas_mapview.UnHighlight_All()
		self.owner_ref.canvas_mapview.Highlight_Segments( [row_number] )
		self.owner_ref.Update_Selected_Segment_Properties( row_number )


	def UnHighlight_All_Rows( self ):
		for row,handler in self.start_x_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.start_y_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.end_x_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.end_y_handler_dict.items():
			handler.configure( background = "white", foreground = "black", font=self.orig_font )
		for row,handler in self.type_handler_dict.items():
			handler.configure( foreground = "black", font=self.orig_font )
		for row,handler in self.invis_handler_dict.items():
			handler.configure( foreground = "black", font=self.orig_font )


	def Apply_Selected_Row_Changes( self, selected_row ):
		# When a segment is selected on the table, and some values are changed in the properties frame, this function applies the changes to the "segment dictionary"
		# Only to be taken into account in the segment edit mode
		if self.owner_ref.current_mode == rceditor_user_interface.Mode.segment and self.owner_ref.current_segment_submode == rceditor_user_interface.Segment_SubMode.edit:
			logging.debug( "Funcion Apply_Selected_Row_Changes llamada, para la fila " + str(selected_row) + ", + se intentan aplicar los cambios al diccionario." )
			try:
				# Read selected segment
				segm_number = selected_row
				# Get segment coordinates
				self.map_ref.segment_dict.get(segm_number).start.x = float( self.start_x_handler_dict.get( segm_number ).get() )
				self.map_ref.segment_dict.get(segm_number).start.y = float( self.start_y_handler_dict.get( segm_number ).get() )
				self.map_ref.segment_dict.get(segm_number).end.x = float( self.end_x_handler_dict.get( segm_number ).get() )
				self.map_ref.segment_dict.get(segm_number).end.y = float( self.end_y_handler_dict.get( segm_number ).get() )

				# Get segment type
				read_segm_type = self.type_variable_dict.get(segm_number).get()
				for type_num, segm_type_to_compare in enumerate(self.segm_type_choices, start=0) :
					if read_segm_type == segm_type_to_compare:
						self.map_ref.segment_dict.get(segm_number).segm_type = type_num
						break	# Exit for
				# Get segment visibility
				self.map_ref.segment_dict.get(segm_number).invisible = self.invis_variable_dict.get(segm_number).get()  
				# Update canvas display on main window editor
				self.owner_ref.canvas_mapview.Update_Segments_Display( [segm_number], self.map_ref )
				self.owner_ref.canvas_mapview.Highlight_Segments( [segm_number] )		# Type cast into list. After update, we need to highlight again
				self.owner_ref.Update_Selected_Segment_Properties( segm_number )
				# Update table contents again (to check program consistency)
				self.update_table_row_values_from_map( selected_row )

				logging.debug( "Modificaciones segmento leidas desde tabla: segm_num = " + str(segm_number) + \
						", start: x= " + str(self.map_ref.segment_dict.get(segm_number).start.x) + \
						", y= " + str( self.map_ref.segment_dict.get(segm_number).start.y ) + \
						", end: x= " + str(self.map_ref.segment_dict.get(segm_number).end.x) + \
						", y= " + str( self.map_ref.segment_dict.get(segm_number).end.y) + \
						". Tipo = " + str( type_num ) + "(" + read_segm_type + ")" + \
						". Invisible = " + str( self.map_ref.segment_dict.get(segm_number).invisible ) )
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title="Error", message="Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: " + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Selected_Row_Changes llamada, pero en el modo incorrecto. No se hace nada." )



	def Segment_Table_RealNumber_FocusOut_Callback( self, event ):
		# This is the callback function called everytime an entry widget loses focus
		selected_widget_handler = event.widget
		logging.debug( "Llamada a función Segment_Table_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) + \
				", widget_name = " + str(selected_widget_handler) )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.segment:
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
					tk.messagebox.showerror(title="Error", message="Valor no válido, no es un número. No se tienen en cuenta las modificaciones.")
					#return(False)
			else:
				logging.debug("FocusOut: Modo incorrecto. No se hace nada.")
				#return(False)	
		else:
			logging.debug("FocusOut: Mapa no cargado. No se hace nada")
			#return(False)

	



	def Segment_Table_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Table_Checkbox_Click_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.segment:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")




	def Segment_Table_OptionMenu_Click_Callback( self, ChosenOption ):
		# This function will be called when a OptionMenu on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Property_OptionMenu_Click_Callback: Modo = " + rceditor_user_interface.mode_names.get( self.owner_ref.current_mode ) + \
				", opcion elegida: " + ChosenOption )
		if self.owner_ref.map_loaded == True:
			if self.owner_ref.current_mode == rceditor_user_interface.Mode.segment:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def Delete_Selected_Segment( self ):
		# When a segment is selected and the delete button is pressed, this function makes the actions to delete it.
		if self.owner_ref.map_loaded == True:
			if self.selected_row_number is not None:
				answer = tk.messagebox.askyesnocancel("Eliminar segmento", "¿Desea eliminar el segmento numero " + str(self.selected_row_number) + "?")
				logging.debug( "Pregunta eliminar segmento, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.owner_ref.mapa_cargado.DeleteSegment( self.selected_row_number )
				self.owner_ref.mapa_cargado.Segments_Reenumerate()
				self.owner_ref.canvas_mapview.DrawAll( self.owner_ref.mapa_cargado )
				self.owner_ref.Unselect_All()
				self.owner_ref.window_statusbar.set_field_1("%s %s %s", "Segmento ", self.selected_row_number , " borrado" )
				# Redraw table
				self.update_table_from_map_editor()
				# No segment is selected (4/7/2021)
				self.selected_row_number = None
			else:
				tk.messagebox.showerror(title="Error", message="Ninguna fila seleccionada.")
				logging.debug( "En funcion Delete_Selected_Segment, error: ninguna fila seleccionada." )

		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")



	def New_Row_At_End_Of_Table( self ):
		# This function creates a new row at the table, and declares this as a new segment
		if self.owner_ref.map_loaded == True:
			# Before doing anything, we apply the currently selected row changes (or we will lose them) (4/7/2021)
			if self.selected_row_number is not None:
				self.Apply_Selected_Row_Changes( self.selected_row_number )
			# Unselect everything
			self.UnHighlight_All_Rows()
			self.selected_row_number = None
			# Declare new segment data (with default values)
			new_segment = rceditor_maps.Segment( start=rceditor_maps.Point(x=0,y=0), end=rceditor_maps.Point(x=100,y=100), segm_type=rceditor_maps.Segment_Type.wall.value, invisible=False)
			# Create new segment
			self.map_ref.AddSegment( new_segment )
			# Update main window editor canvas
			self.owner_ref.canvas_mapview.DrawSingleSegment( Map=self.map_ref, num_segm=self.map_ref.segment_number-1 )
			self.owner_ref.canvas_mapview.DrawSingleSegmentNumber( Map=self.map_ref, num_segm=self.map_ref.segment_number-1 )
			# Update table
			self.update_table_from_map_editor()
			# Move canvas to lower position (4/7/2021)
			self.frame_table_frame.ScrollToBottom()

