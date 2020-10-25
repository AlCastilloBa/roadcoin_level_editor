
import tkinter as tk
from tkinter import ttk		# Textbox
from PIL import ImageTk, Image		# Pillow
# from tkinter import filedialog
import logging


import scrframe

import rceditor_maps



def do_nothing():
	x = 0



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
		self.button_new_row = tk.Button(master=self.frame_upper_buttons, text="Nueva fila", image = self.img_new_row_icon, compound = tk.LEFT, command = do_nothing )
		self.button_new_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		self.button_delete_row = tk.Button(master=self.frame_upper_buttons, text="Eliminar fila", image = self.img_delete_row_icon, compound = tk.LEFT, command = do_nothing )
		self.button_delete_row.pack( side=tk.LEFT, fill=tk.BOTH, expand=False )
		self.button_update_canvas = tk.Button(master=self.frame_upper_buttons, text="Actualizar mapa editor (desde tabla)", image = self.img_update_icon, compound = tk.LEFT, command = do_nothing )
		self.button_update_canvas.pack( side=tk.TOP, fill=tk.BOTH, expand=False )
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

		#for row in range(0, Map.segment_number-1):
		#	logging.debug( "Tabla de segmentos, añadiendo fila " + str( row ) )
		#	
		#	self.frame_table_frame.interior.rowconfigure( row, weight=1 )	# Esto es asi o es en interior ??????????????
		#	# Segment number
		#	segm_num_ref = tk.Label( master = self.frame_table_frame.interior, text=str( row ), width = 3 )
		#	self.segm_number_handler_dict.setdefault( row , segm_num_ref )
		#	segm_num_ref.grid( row=row, column=0,  padx=0, pady=0, sticky="nsew" )
		#	# Start X
		#	start_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
		#	start_x_ref.insert(0, Map.segment_dict.get( row ).start.x )
		#	self.start_x_handler_dict.setdefault( row , start_x_ref )
		#	start_x_ref.grid( row=row, column=1,  padx=0, pady=0, sticky="nsew" )
		#	# Start Y
		#	start_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
		#	start_y_ref.insert(0, Map.segment_dict.get( row ).start.y )
		#	self.start_y_handler_dict.setdefault( row , start_y_ref )
		#	start_y_ref.grid( row=row, column=2,  padx=0, pady=0, sticky="nsew" )
		#	# End X
		#	end_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
		#	end_x_ref.insert(0, Map.segment_dict.get( row ).end.x )
		#	self.end_x_handler_dict.setdefault( row , end_x_ref )
		#	end_x_ref.grid( row=row, column=3,  padx=0, pady=0, sticky="nsew" )
		#	# End Y
		#	end_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
		#	end_y_ref.insert(0, Map.segment_dict.get( row ).end.y )
		#	self.end_y_handler_dict.setdefault( row , end_y_ref )		
		#	end_y_ref.grid( row=row, column=4,  padx=0, pady=0, sticky="nsew" )	
		#	# Type
		#	type_variable = tk.StringVar()
		#	type_ref = tk.OptionMenu( self.frame_table_frame.interior, type_variable, *self.segm_type_choices )
		#	type_variable.set( self.segm_type_choices[ Map.segment_dict.get(row).segm_type ] )
		#	type_ref.configure( width = 12 )
		#	self.type_handler_dict.setdefault( row , type_ref )
		#	self.type_variable_dict.setdefault( row , type_variable )
		#	type_ref.grid( row=row, column=5,  padx=0, pady=0, sticky="nsew" )
		#	# Invis
		#	invis_variable = tk.BooleanVar()
		#	invis_ref = tk.Checkbutton(master=self.frame_table_frame.interior, text="Invisible", var=invis_variable, width = 12 )
		#	if Map.segment_dict.get(row).invisible == True:
		#		invis_ref.select()
		#	else:
		#		invis_ref.deselect()
		#	self.invis_handler_dict.setdefault( row , invis_ref )
		#	self.invis_variable_dict.setdefault( row , invis_variable )
		#	invis_ref.grid( row=row, column=6,  padx=0, pady=0, sticky="nsew" )


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
		# self.SegmentTableWindow.destroy()
		self.map_ref = None
		self.owner_ref = None
		self.__del__()
		del self


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
		# This function updates table contents from map data to the table
		self.delete_table_widgets()
		# Create the table elements
		for row in range(0, self.map_ref.segment_number-1):
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
			# Start Y
			start_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			start_y_ref.insert(0, self.map_ref.segment_dict.get( row ).start.y )
			self.start_y_handler_dict.setdefault( row , start_y_ref )
			start_y_ref.grid( row=row, column=2,  padx=0, pady=0, sticky="nsew" )
			# End X
			end_x_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			end_x_ref.insert(0, self.map_ref.segment_dict.get( row ).end.x )
			self.end_x_handler_dict.setdefault( row , end_x_ref )
			end_x_ref.grid( row=row, column=3,  padx=0, pady=0, sticky="nsew" )
			# End Y
			end_y_ref = ttk.Entry(master = self.frame_table_frame.interior, width = 15 )
			end_y_ref.insert(0, self.map_ref.segment_dict.get( row ).end.y )
			self.end_y_handler_dict.setdefault( row , end_y_ref )		
			end_y_ref.grid( row=row, column=4,  padx=0, pady=0, sticky="nsew" )	
			# Type
			type_variable = tk.StringVar()
			type_ref = tk.OptionMenu( self.frame_table_frame.interior, type_variable, *self.segm_type_choices )
			type_variable.set( self.segm_type_choices[ self.map_ref.segment_dict.get(row).segm_type ] )
			type_ref.configure( width = 12 )
			self.type_handler_dict.setdefault( row , type_ref )
			self.type_variable_dict.setdefault( row , type_variable )
			type_ref.grid( row=row, column=5,  padx=0, pady=0, sticky="nsew" )
			# Invis
			invis_variable = tk.BooleanVar()
			invis_ref = tk.Checkbutton(master=self.frame_table_frame.interior, text="Invisible", var=invis_variable, width = 12 )
			if self.map_ref.segment_dict.get(row).invisible == True:
				invis_ref.select()
			else:
				invis_ref.deselect()
			self.invis_handler_dict.setdefault( row , invis_ref )
			self.invis_variable_dict.setdefault( row , invis_variable )
			invis_ref.grid( row=row, column=6,  padx=0, pady=0, sticky="nsew" )


	def update_map_editor_from_table( self ):
		# This function updates map data and forces a full map redraw
		pass




	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de tabla de segmentos" )
		self.img_new_row_icon = ImageTk.PhotoImage(Image.open("icons/new_row-16.png"))   # PIL solution
		self.img_delete_row_icon = ImageTk.PhotoImage(Image.open("icons/delete_row-16.png"))
		self.img_update_icon = ImageTk.PhotoImage(Image.open("icons/reload-16.png"))



