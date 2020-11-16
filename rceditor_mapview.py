
import tkinter as tk
from PIL import ImageTk, Image, ImageEnhance		# Pillow
import logging
import sys
import math

from rceditor_maps import Segment_Type, Segment_Type_Names


def do_nothing():
	x = 0


class Canvas_WithScrollbars(tk.Frame):
	zoomlevel = 1.0
	segment_lines_dict = dict()	# Dictionary that links canvas lines and segments
	segment_num_texts_dict = dict()	# Dictionary that links canvas texts and segments
	bumpers_dict = dict()		# Dictionary that links canvas circles and bumpers
	bumpers_num_texts_dict = dict()	# Dictionary that links canvas texts and bumpers
	raccz_dict = dict()		# Dictionary that links canvas lines and round acceleration zones
	raccz_circles_dict = dict()	# Dictionary that links canvas circles and round acceleration zones
	raccz_num_texts_dict = dict()	# Dictionary that links canvas texts and round acceleration zones
	rotbg_canvas_object_ref = None	# Rotating background canvas reference
	rotbg_image = None		# Rotating background image (PIL image object)
	rotbg_image_resized = None	# Rotating background resized image (PIL Photoimage object)


	def __init__(self, master, owner_object ):
		tk.Frame.__init__(self, master)
		self.master = master		# Store reference to master
		self.owner_object = owner_object	# Store reference to the object that owns this "Canvas_WithScrollbars"
		self.rowconfigure( 0, weight=1 ) #, minsize=500)
		self.rowconfigure( 1, weight=0, minsize=20)
		self.columnconfigure( 0, weight=1 ) #, minsize=500)
		self.columnconfigure( 1, weight=0, minsize=20)

		self.viewer = tk.Canvas( master = self )

		self.hbar = tk.Scrollbar(master = self, orient=tk.HORIZONTAL)
		self.hbar.config( command = self.viewer.xview )

		self.vbar = tk.Scrollbar(master = self, orient=tk.VERTICAL)
		self.vbar.config( command = self.viewer.yview )

		# self.canvas_viewer.config(width=300,height=300)
		self.viewer.config( xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set )

		self.img_zoom_icon = ImageTk.PhotoImage(Image.open("icons/magn_glass-16.png"))  # PIL solution
		self.zoom_button = tk.Button( master = self, image = self.img_zoom_icon, command = self.ZoomButtonPressed )

		self.viewer.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
		self.hbar.grid (row=1, column=0, padx=0, pady=0, sticky="nsew")
		self.vbar.grid (row=0, column=1, padx=0, pady=0, sticky="nsew")
		self.zoom_button.grid (row=1, column=1, padx=0, pady=0, sticky="nsew")

		# Save original canvas color in order to restore it later
		self.orig_viewer_color = self.viewer.cget("background")

	
	def ZoomButtonPressed( self ):
		logging.debug( "Abriendo ventana seleccion de zoom" )
		self.zoom_select_window = ZoomLevelSelectWindow( master = self.master, owner_object=self.owner_object )

	def ClearViewer( self ):
		self.viewer.delete("all")
		self.segment_lines_dict.clear()
		self.segment_num_texts_dict.clear()

	def DisableViewer( self ):
		self.viewer.delete("all")
		self.segment_lines_dict.clear()
		self.segment_num_texts_dict.clear()
		self.viewer.config( background=self.orig_viewer_color )



	def DrawAllSegments( self, Map ):
		logging.debug( "Comenzando representacion de segmentos" )
		self.viewer.config( background="white" )
		for num_segm, segm in Map.segment_dict.items():
			self.DrawSingleSegment( Map, num_segm )


	def DrawSingleSegment( self, Map, num_segm ):
		# ref_linea = self.viewer.create_line(segm.start.x * self.zoomlevel, segm.start.y*self.zoomlevel, segm.end.x*self.zoomlevel, segm.end.y*self.zoomlevel)
		ref_linea = self.viewer.create_line( 	Map.segment_dict.get(num_segm).start.x * self.zoomlevel, \
							Map.segment_dict.get(num_segm).start.y * self.zoomlevel, \
							Map.segment_dict.get(num_segm).end.x * self.zoomlevel, \
							Map.segment_dict.get(num_segm).end.y * self.zoomlevel)
		# Add to dictionary for later use
		self.segment_lines_dict.setdefault(ref_linea, num_segm)	
		logging.debug( "Dibujando segmento " + str(num_segm) + ", ref linea = " + str(ref_linea) )
		# Set color according to segment type
		if Map.segment_dict.get(num_segm).segm_type == Segment_Type.wall.value:
			self.viewer.itemconfig( ref_linea, fill="black")
		elif Map.segment_dict.get(num_segm).segm_type == Segment_Type.goal.value:
			self.viewer.itemconfig( ref_linea, fill="green")
		elif Map.segment_dict.get(num_segm).segm_type == Segment_Type.death.value:
			self.viewer.itemconfig( ref_linea, fill="red")
		elif Map.segment_dict.get(num_segm).segm_type == Segment_Type.pinball_flipper_L.value:
			self.viewer.itemconfig( ref_linea, fill="blue")
		elif Map.segment_dict.get(num_segm).segm_type == Segment_Type.pinball_flipper_R.value:
			self.viewer.itemconfig( ref_linea, fill="blue")
		else:
			logging.debug( "Al dar color al segmento " + str(num_segm) + ", tipo de segmento " + str(Map.segment_dict.get(num_segm).segm_type) + " no es conocido.")
		# Set dash pattern according to visibility
		if Map.segment_dict.get(num_segm).invisible == True:
			self.viewer.itemconfig( ref_linea, dash=(3,3) )		# Dashed line: 3 pix line, 3 pix gap
		else:
			self.viewer.itemconfig( ref_linea, dash=() )	# Solid line



	def DrawAllSegmentNumbers( self, Map ):
		logging.debug( "Comenzando representacion de números de segmentos" )
		self.viewer.config( background="white" )
		for num_segm, segm in Map.segment_dict.items():
			self.DrawSingleSegmentNumber( Map, num_segm ) 


	def DrawSingleSegmentNumber( self, Map, num_segm ):
		ref_texto = self.viewer.create_text( 	self.zoomlevel*(Map.segment_dict.get(num_segm).start.x + Map.segment_dict.get(num_segm).end.x)/2 , \
							self.zoomlevel*(Map.segment_dict.get(num_segm).start.y + Map.segment_dict.get(num_segm).end.y)/2 , \
							text=num_segm )
		# Add to dictionary for later use
		self.segment_num_texts_dict.setdefault(ref_texto, num_segm)
		logging.debug( "Dibujando numero segmento " + str(num_segm) + ", ref texto = " + str(ref_texto) )	


	def DrawAll( self, Map ):
		logging.debug( "Procediendo a redibujar todo" )
		self.ClearViewer()
		self.Draw_RotBG( Map )
		self.DrawAllSegments( Map )
		self.DrawAllSegmentNumbers( Map )
		self.DrawAllBumpers( Map )
		self.DrawAllBumpersNumbers( Map )
		self.DrawAllRACCZ( Map)
		self.DrawAllRACCZNumbers( Map )


	def UnHighlight_All( self ):
		logging.debug( "Procediendo a deseleccionar todo" )
		self.UnHighlight_Segments()
		self.UnHighlight_Bumpers()
		self.UnHighlight_RACCZ()


	def GoTo_Origin( self ):
		self.viewer.xview(tk.MOVETO, 0)
		self.viewer.yview(tk.MOVETO, 0)


	def UnHighlight_Segments( self ):
		logging.debug( "Marcando todos los segmentos como no seleccionados." )
		for line_ref in self.segment_lines_dict:
			#self.viewer.itemconfig( line_ref, fill="black")
			self.viewer.itemconfig( line_ref, width=1)
		for text_ref in self.segment_num_texts_dict:
			#self.viewer.itemconfig( text_ref, fill="black")
			pass	# TODO Falta poner fuente estandar


	def Highlight_Segments( self, segm_list_to_highlight ):
		logging.debug( "Marcando como seleccionados los segmentos: " + str(segm_list_to_highlight) )
		if segm_list_to_highlight:	# If the list is not empty
			for segm in segm_list_to_highlight:
				# Inverse lookup in dictionary to get canvas lines and text references
				# Note: this could be slow !!
				line_ref = next( line_ref for line_ref, value in self.segment_lines_dict.items() if value == segm )
				text_ref = next( text_ref for text_ref, value in self.segment_num_texts_dict.items() if value == segm )
				logging.debug( "Marcando segmento " + str(segm) + " con referencia de linea " + str(line_ref) )
				#self.viewer.itemconfig( line_ref, fill="red")
				self.viewer.itemconfig( line_ref, width=3)
				logging.debug( "Marcando texto segmento " + str(segm) + " con referencia de texto " + str(text_ref) )
				#self.viewer.itemconfig( text_ref, fill="red")
				pass	# TODO Falta poner la fuente grande


	def Update_Segments_Display( self, segm_list_to_update, Map ):
		logging.debug( "Actualizando representacion grafica de los segmentos: " + str(segm_list_to_update) )
		if segm_list_to_update:		# If the list is not empty
			for segm in segm_list_to_update:
				# Inverse lookup in dictionary to get canvas lines and text references
				# Note: this could be slow !!
				line_ref = next( line_ref for line_ref, value in self.segment_lines_dict.items() if value == segm )
				text_ref = next( text_ref for text_ref, value in self.segment_num_texts_dict.items() if value == segm )
				# Delete old line and text from canvas
				self.viewer.delete( line_ref )
				self.viewer.delete( text_ref )
				# Delete old entries in dictionaries
				del self.segment_lines_dict[ line_ref ]
				del self.segment_num_texts_dict[ text_ref ]
				# Draw new line and text (and this will add entries to dictionaries
				self.DrawSingleSegment( Map, segm )
				self.DrawSingleSegmentNumber( Map, segm )


	def Load_Images( self, Map, preferences ):
		if Map.rotating_background == True:
			logging.debug( "Cargando imagenes del mapa" )
			try:
				self.rotbg_image = Image.open( preferences.GamePath + "/" + Map.rotating_background_path  )			# PIL Image Solution --> Can be manipulated (but not used directly for Tkinter)
				# self.rotbg_image = ImageTk.PhotoImage(  Image.open( preferences.GamePath + "/" + Map.rotating_background_path  )  )	# PIL Image + PhotoImage Solution --> Cannot be manipulated (but shown on Tkinter)

			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title="Error", message="No se ha podido cargar la imagen del fondo giratorio.\n\n\nExcepcion: " + str( sys.exc_info()[0] ) + "\n" + str(e) )
			else:
				logging.debug( "Imagen " + preferences.GamePath + "/" + Map.rotating_background_path + " cargada.")
		else:	# TODO Prueba 1/11/2020
			self.rotbg_image = None

	def Draw_RotBG( self, Map ):
		if self.rotbg_image is not None:	# If the image is loaded
			logging.debug( "Creando imagen de fondo giratorio, en x=" + str( Map.rotating_background_left_x_pos ) + ", y=" + str( Map.rotating_background_up_y_pos ) )
			# Resize image and 
			# Note: Keep the reference (if not, the image will be garbage-collected)
			self.rotbg_image_resized = self.rotbg_image.resize( (int(self.rotbg_image.size[0]*self.zoomlevel), int(self.rotbg_image.size[1]*self.zoomlevel)) , Image.LANCZOS )
			# Enhance image: colour, contrast and brightness
			enhancer = ImageEnhance.Color(self.rotbg_image_resized)
			self.rotbg_image_resized = enhancer.enhance( 1.0 )
			enhancer = ImageEnhance.Contrast(self.rotbg_image_resized)
			self.rotbg_image_resized = enhancer.enhance( 0.2 )
			enhancer = ImageEnhance.Brightness(self.rotbg_image_resized)
			self.rotbg_image_resized = enhancer.enhance( 1.5 )
			# Convert to Photoimage (in order to show on Tkinter)
			self.rotbg_image_resized = ImageTk.PhotoImage( self.rotbg_image_resized )
			# Draw image on canvas
			rotbg_canvas_object_ref = self.viewer.create_image( 	int( Map.rotating_background_left_x_pos * self.zoomlevel ), \
										int( Map.rotating_background_up_y_pos * self.zoomlevel ), \
										image=self.rotbg_image_resized ,\
										anchor=tk.NW)


	def DrawAllBumpers( self, Map ):
		logging.debug( "Comenzando representacion de bumpers" )
		self.viewer.config( background="white" )
		for num_bumper, bumper in Map.pinball_bumpers_dict.items():
			self.DrawSingleBumper( Map, num_bumper )


	def DrawSingleBumper( self, Map, num_bumper ):
		center = Map.pinball_bumpers_dict.get(num_bumper).center
		radius = Map.pinball_bumpers_dict.get(num_bumper).radius
		ref_circ = self.viewer.create_oval(		( center.x-radius ) * self.zoomlevel, \
								( center.y-radius ) * self.zoomlevel, \
								( center.x+radius ) * self.zoomlevel, \
								( center.y+radius ) * self.zoomlevel, \
								outline="black") 	
		# Add to dictionary for later use
		self.bumpers_dict.setdefault(ref_circ, num_bumper)	
		logging.debug( "Dibujando bumper " + str(num_bumper) + ", ref circulo = " + str(ref_circ) )


	def DrawAllBumpersNumbers( self, Map ):
		logging.debug( "Comenzando representacion de números de bumpers" )
		self.viewer.config( background="white" )
		for num_bumper, bumper in Map.pinball_bumpers_dict.items():
			self.DrawSingleBumperNumber( Map, num_bumper ) 


	def DrawSingleBumperNumber( self, Map, num_bumper ):
		ref_text = self.viewer.create_text( 	self.zoomlevel * (Map.pinball_bumpers_dict.get(num_bumper).center.x), \
							self.zoomlevel * (Map.pinball_bumpers_dict.get(num_bumper).center.y), \
							text=num_bumper )
		# Add to dictionary for later use
		self.bumpers_num_texts_dict.setdefault(ref_text, num_bumper)
		logging.debug( "Dibujando numero bumper " + str(num_bumper) + ", ref texto = " + str(ref_text) )	


	def UnHighlight_Bumpers( self ):
		logging.debug( "Marcando todos los bumpers como no seleccionados." )
		for circle_ref in self.bumpers_dict:
			#self.viewer.itemconfig( circle_ref, fill="black")
			self.viewer.itemconfig( circle_ref, width=1)
		for text_ref in self.bumpers_num_texts_dict:
			#self.viewer.itemconfig( text_ref, fill="black")
			pass	# TODO Falta poner fuente estandar


	def Highlight_Bumpers( self, bumper_list_to_highlight ):
		logging.debug( "Marcando como seleccionados los bumpers: " + str(bumper_list_to_highlight) )
		if bumper_list_to_highlight:	# If the list is not empty
			for bumper in bumper_list_to_highlight:
				# Inverse lookup in dictionary to get canvas circles and text references
				# Note: this could be slow !!
				circle_ref = next( circle_ref for circle_ref, value in self.bumpers_dict.items() if value == bumper )
				text_ref = next( text_ref for text_ref, value in self.bumpers_num_texts_dict.items() if value == bumper )
				logging.debug( "Marcando bumper " + str(bumper) + " con referencia de circulo " + str(circle_ref) )
				#self.viewer.itemconfig( circle_ref, fill="red")
				self.viewer.itemconfig( circle_ref, width=3)
				logging.debug( "Marcando texto bumper " + str(bumper) + " con referencia de texto " + str(text_ref) )
				#self.viewer.itemconfig( text_ref, fill="red")
				pass	# TODO Falta poner la fuente grande


	def Update_Bumpers_Display( self, bumper_list_to_update, Map ):
		logging.debug( "Actualizando representacion grafica de los bumpers: " + str(bumper_list_to_update) )
		if bumper_list_to_update:		# If the list is not empty
			for bumper in bumper_list_to_update:
				# Inverse lookup in dictionary to get canvas circles and text references
				# Note: this could be slow !!
				circle_ref = next( circle_ref for circle_ref, value in self.bumpers_dict.items() if value == bumper )
				text_ref = next( text_ref for text_ref, value in self.bumpers_num_texts_dict.items() if value == bumper )
				# Delete old line and text from canvas
				self.viewer.delete( circle_ref )
				self.viewer.delete( text_ref )
				# Delete old entries in dictionaries
				del self.bumpers_dict[ circle_ref ]
				del self.bumpers_num_texts_dict[ text_ref ]
				# Draw new line and text (and this will add entries to dictionaries)
				self.DrawSingleBumper( Map, bumper )
				self.DrawSingleBumperNumber( Map, bumper )




	def DrawAllRACCZ( self, Map ):
		logging.debug( "Comenzando representacion de zonas de aceleración circulares" )
		self.viewer.config( background="white" )
		for num_raccz, raccz in Map.dict_round_acel_zones.items():
			self.DrawSingleRACCZ( Map, num_raccz )


	def DrawSingleRACCZ( self, Map, num_raccz ):
		center = Map.dict_round_acel_zones.get(num_raccz).center
		radius = Map.dict_round_acel_zones.get(num_raccz).radius
		angle = Map.dict_round_acel_zones.get(num_raccz).angle
		# Draw an arrow like triangle
		ref_polygon = self.viewer.create_line( 		(center.x + radius*math.cos(math.radians( angle -90 + 0   ) ) ) * self.zoomlevel, \
								(center.y + radius*math.sin(math.radians( angle -90 + 0   ) ) ) * self.zoomlevel, \
								(center.x + radius*math.cos(math.radians( angle -90 + 160 ) ) ) * self.zoomlevel, \
								(center.y + radius*math.sin(math.radians( angle -90 + 160 ) ) ) * self.zoomlevel, \
								(center.x + radius*math.cos(math.radians( angle -90 - 160 ) ) ) * self.zoomlevel, \
								(center.y + radius*math.sin(math.radians( angle -90 - 160 ) ) ) * self.zoomlevel, \
								(center.x + radius*math.cos(math.radians( angle -90 + 0   ) ) ) * self.zoomlevel, \
								(center.y + radius*math.sin(math.radians( angle -90 + 0   ) ) ) * self.zoomlevel, \
								fill = "purple"     )
		# Draw a circle
		ref_circle = self.viewer.create_oval(		( center.x-radius ) * self.zoomlevel, \
								( center.y-radius ) * self.zoomlevel, \
								( center.x+radius ) * self.zoomlevel, \
								( center.y+radius ) * self.zoomlevel, \
								outline="purple") 	
		# Add to dictionary for later use
		self.raccz_dict.setdefault(ref_polygon, num_raccz)	
		self.raccz_circles_dict.setdefault(ref_circle, num_raccz)
		logging.debug( "Dibujando zona de aceleracion circular " + str(num_raccz) + ", ref linea = " + str(ref_polygon) )
		# Set dash pattern according to visibility
		if Map.dict_round_acel_zones.get(num_raccz).invisible == True:
			self.viewer.itemconfig( ref_polygon, dash=(3,3) )		# Dashed line: 3 pix line, 3 pix gap
			self.viewer.itemconfig( ref_circle, dash=(3,3) )
		else:
			self.viewer.itemconfig( ref_polygon, dash=() )	# Solid line
			self.viewer.itemconfig( ref_circle, dash=() )


	def DrawAllRACCZNumbers(self, Map ):
		logging.debug( "Comenzando representacion de números de zonas de aceleración circular" )
		self.viewer.config( background="white" )
		for num_raccz, raccz in Map.dict_round_acel_zones.items():
			self.DrawSingleRACCZNumber( Map, num_raccz ) 


	def DrawSingleRACCZNumber(self, Map, num_raccz):
		ref_text = self.viewer.create_text( 	self.zoomlevel * (Map.dict_round_acel_zones.get(num_raccz).center.x), \
							self.zoomlevel * (Map.dict_round_acel_zones.get(num_raccz).center.y), \
							text=num_raccz, fill="purple" )
		# Add to dictionary for later use
		self.raccz_num_texts_dict.setdefault(ref_text, num_raccz)
		logging.debug( "Dibujando numero zona de aceleración circular " + str(num_raccz) + ", ref texto = " + str(ref_text) )



	def UnHighlight_RACCZ( self ):
		logging.debug( "Marcando todos las zonas circulares de aceleración como no seleccionadas." )
		for polygon_ref in self.raccz_dict:
			#self.viewer.itemconfig( polygon_ref, fill="black")
			self.viewer.itemconfig( polygon_ref, width=1)
		for circle_ref in self.raccz_circles_dict:
			#self.viewer.itemconfig( circle_ref, fill="black")
			self.viewer.itemconfig( circle_ref, width=1)			
		for text_ref in self.raccz_num_texts_dict:
			#self.viewer.itemconfig( text_ref, fill="black")
			pass	# TODO Falta poner fuente estandar


	def Highlight_RACCZ( self, raccz_list_to_highlight ):
		logging.debug( "Marcando como seleccionados las zonas de aceleración circulares: " + str(raccz_list_to_highlight) )
		if raccz_list_to_highlight:	# If the list is not empty
			for raccz in raccz_list_to_highlight:
				# Inverse lookup in dictionary to get canvas polygons, lines and text references
				# Note: this could be slow !!
				polygon_ref = next( polygon_ref for polygon_ref, value in self.raccz_dict.items() if value == raccz )
				circle_ref = next( circle_ref for circle_ref, value in self.raccz_circles_dict.items() if value == raccz )
				text_ref = next( text_ref for text_ref, value in self.raccz_num_texts_dict.items() if value == raccz )
				logging.debug( "Marcando zona de aceleración circular " + str(raccz) + " con referencia de poligono " + str(polygon_ref) )
				#self.viewer.itemconfig( line_ref, fill="red")
				self.viewer.itemconfig( polygon_ref, width=3)
				logging.debug( "Marcando zona de aceleración circular " + str(raccz) + " con referencia de circulo " + str(circle_ref) )
				#self.viewer.itemconfig( circle_ref, fill="red")
				self.viewer.itemconfig( circle_ref, width=3)
				logging.debug( "Marcando texto zona de aceleración circular " + str(raccz) + " con referencia de texto " + str(text_ref) )
				#self.viewer.itemconfig( text_ref, fill="red")
				pass	# TODO Falta poner la fuente grande


	def Update_RACCZ_Display( self, raccz_list_to_update, Map ):
		logging.debug( "Actualizando representacion grafica de las zonas de aceleración circulares: " + str(raccz_list_to_update) )
		if raccz_list_to_update:		# If the list is not empty
			for raccz in raccz_list_to_update:
				# Inverse lookup in dictionary to get canvas polygons, circles and text references
				# Note: this could be slow !!
				polygon_ref = next( polygon_ref for polygon_ref, value in self.raccz_dict.items() if value == raccz )
				circle_ref = next( circle_ref for circle_ref, value in self.raccz_circles_dict.items() if value == raccz )
				text_ref = next( text_ref for text_ref, value in self.raccz_num_texts_dict.items() if value == raccz )
				# Delete old line and text from canvas
				self.viewer.delete( polygon_ref )
				self.viewer.delete( circle_ref )
				self.viewer.delete( text_ref )
				# Delete old entries in dictionaries
				del self.raccz_dict[ polygon_ref ]
				del self.raccz_circles_dict[ circle_ref ]
				del self.raccz_num_texts_dict[ text_ref ]
				# Draw new line and text (and this will add entries to dictionaries
				self.DrawSingleRACCZ( Map, raccz )
				self.DrawSingleRACCZNumber( Map, raccz )


	def Set_Cursor_Arrow( self ):
		self.viewer.config( cursor="arrow" )

	def Set_Cursor_Cross( self ):
		self.viewer.config( cursor="tcross" )










#########################################################################3


class ZoomLevelSelectWindow():

	def __init__( self, master, owner_object ):
		self.owner_object = owner_object	# Store reference to the object that owns this "Canvas_WithScrollbars"

		self.ZoomWindow = tk.Toplevel( master )
		self.ZoomWindow.transient( master )		# Make this window be child of parent
		self.ZoomWindow.grab_set()			# Make this window Modal
		self.ZoomWindow.protocol('WM_DELETE_WINDOW',do_nothing)		# Close window button behaviour
		# self.PrefWindow.attributes('-topmost', 'true')		# Stay on top of all others
		self.ZoomWindow.title("Seleccione zoom...")

		self.Load_UI_Icons()

		self.radio_buttons_zoom_variable = tk.IntVar()

		# self.radiobutton_zoom_2000 = tk.Radiobutton(master=self.ZoomWindow, text="2000%", variable=self.radio_buttons_zoom_variable, value=2000, command=self.RadioButtonClicked )
		self.radiobutton_zoom_1000 = tk.Radiobutton(master=self.ZoomWindow, text="1000%", variable=self.radio_buttons_zoom_variable, value=1000, command=self.RadioButtonClicked )
		self.radiobutton_zoom_500 = tk.Radiobutton(master=self.ZoomWindow, text="500%", variable=self.radio_buttons_zoom_variable, value=500, command=self.RadioButtonClicked )
		self.radiobutton_zoom_200 = tk.Radiobutton(master=self.ZoomWindow, text="200%", variable=self.radio_buttons_zoom_variable, value=200, command=self.RadioButtonClicked )
		self.radiobutton_zoom_100 = tk.Radiobutton(master=self.ZoomWindow, text="100%", variable=self.radio_buttons_zoom_variable, value=100, command=self.RadioButtonClicked )
		self.radiobutton_zoom_75 = tk.Radiobutton(master=self.ZoomWindow, text="75%", variable=self.radio_buttons_zoom_variable, value=75, command=self.RadioButtonClicked )
		self.radiobutton_zoom_50 = tk.Radiobutton(master=self.ZoomWindow, text="50%", variable=self.radio_buttons_zoom_variable, value=50, command=self.RadioButtonClicked )
		self.radiobutton_zoom_25 = tk.Radiobutton(master=self.ZoomWindow, text="25%", variable=self.radio_buttons_zoom_variable, value=25, command=self.RadioButtonClicked )

		self.radiobuttons_list = [ self.radiobutton_zoom_1000, self.radiobutton_zoom_500, self.radiobutton_zoom_200, self.radiobutton_zoom_100, self.radiobutton_zoom_75, self.radiobutton_zoom_50, self.radiobutton_zoom_25 ] 

		for rb in self.radiobuttons_list:
			rb.pack( side=tk.TOP, padx=2, pady=2 )

		self.frame_accept_cancel = tk.Frame( master=self.ZoomWindow )
		self.button_accept = tk.Button(master=self.frame_accept_cancel, text="Aceptar", image = self.img_green_tick_icon, compound = tk.LEFT, command = self.AcceptButton,  state=tk.DISABLED )
		self.button_cancel = tk.Button(master=self.frame_accept_cancel, text="Cancelar", image = self.img_red_x_icon, compound = tk.LEFT, command = self.CancelButton )

		self.button_accept.grid( row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.button_cancel.grid( row=0, column=1,  padx=2, pady=2, sticky="nsew" )

		self.frame_accept_cancel.columnconfigure( [0, 1], weight=1)
		self.frame_accept_cancel.rowconfigure( 0, weight=1 )

		self.frame_accept_cancel.pack( side=tk.TOP, padx=2, pady=2 )



	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de zoom" )
		self.img_green_tick_icon = ImageTk.PhotoImage(Image.open("icons/green_tick-16.png"))
		self.img_red_x_icon = ImageTk.PhotoImage(Image.open("icons/red_x_icon-16.png"))


	def RadioButtonClicked( self ):
		# Some zoom radio button was clicked, the accept button is now enabled
		self.button_accept.config( state=tk.NORMAL )


	def AcceptButton( self ):
		# (TODO) Cambiar el zoom realmente. Atencion, a que hay que acceder al objeto padre
		self.owner_object.SetZoomLevel( float( self.radio_buttons_zoom_variable.get() )/100 )
		self.ZoomWindow.destroy()
		del self

	def CancelButton( self ):
		self.ZoomWindow.destroy()
		del self




