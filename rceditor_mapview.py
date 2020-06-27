
import tkinter as tk
from PIL import ImageTk, Image		# Pillow
import logging


def do_nothing():
	x = 0


class Canvas_WithScrollbars(tk.Frame):
	zoomlevel = 1.0

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

	def DisableViewer( self ):
		self.viewer.delete("all")
		self.viewer.config( background=self.orig_viewer_color )


	def DrawSegments( self, Map ):
		logging.debug( "Comenzando representacion de segmentos" )
		self.viewer.config( background="white" )
		for num_segm, segm in Map.segment_dict.items():
			logging.debug( "Dibujando segmento " + str(num_segm) )
			self.viewer.create_line(segm.start.x * self.zoomlevel, segm.start.y*self.zoomlevel, segm.end.x*self.zoomlevel, segm.end.y*self.zoomlevel)


	def DrawSegmentNumbers( self, Map ):
		logging.debug( "Comenzando representacion de números de segmentos" )
		self.viewer.config( background="white" )
		for num_segm, segm in Map.segment_dict.items():
			logging.debug( "Dibujando numero segmento " + str(num_segm) )
			self.viewer.create_text( self.zoomlevel*(segm.start.x + segm.end.x)/2 , self.zoomlevel*(segm.start.y + segm.end.y)/2 , text=num_segm )

	def DrawAll( self, Map ):
		logging.debug( "Procediendo a redibujar todo" )
		self.ClearViewer()
		self.DrawSegments( Map )
		self.DrawSegmentNumbers( Map )


