
import tkinter as tk
from PIL import ImageTk, Image		# Pillow
import logging

from rceditor_maps import Segment_Type, Segment_Type_Names


def do_nothing():
	x = 0


class Canvas_WithScrollbars(tk.Frame):
	zoomlevel = 1.0
	segment_lines_dict = dict()	# Dictionary that links canvas lines and segments
	segment_num_texts_dict = dict()	# Dictionary that links canvas texts and segments

	def __init__(self, master):
		tk.Frame.__init__(self, master)
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
		self.zoom_button = tk.Button( master = self, image = self.img_zoom_icon, command = do_nothing )

		self.viewer.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
		self.hbar.grid (row=1, column=0, padx=0, pady=0, sticky="nsew")
		self.vbar.grid (row=0, column=1, padx=0, pady=0, sticky="nsew")
		self.zoom_button.grid (row=1, column=1, padx=0, pady=0, sticky="nsew")

		# Save original canvas color in order to restore it later
		self.orig_viewer_color = self.viewer.cget("background")

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
		self.DrawAllSegments( Map )
		self.DrawAllSegmentNumbers( Map )


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



