# coding=UTF-8

import tkinter as tk
from PIL import ImageTk, Image		# Pillow
import logging

import rceditor_lang



def do_nothing():
	x = 0


class AboutWindow():
	
	def __init__( self, master ):

		# Activate translations language (TODO 21/7/2021)
		_ = rceditor_lang.Get_Current_Gettext_Function()

		self.AboutWindow = tk.Toplevel( master )
		self.AboutWindow.transient( master )		# Make this window be child of parent
		self.AboutWindow.grab_set()			# Make this window Modal
		# self.AboutWindow.protocol('WM_DELETE_WINDOW',do_nothing)		# Close window button behaviour
		# self.PrefWindow.attributes('-topmost', 'true')		# Stay on top of all others
		self.AboutWindow.resizable( False, False )	# Not resizable
		self.AboutWindow.title(  _("Acerca de...")  )

		self.Load_UI_Icons()
		
		self.canvas_logo_image = tk.Canvas( master = self.AboutWindow, width = self.orig_logo_image_size_width, height = self.orig_logo_image_size_height )
		self.Draw_Logo_On_Canvas()

		self.label_credits_text = tk.Label(master=self.AboutWindow, \
			text=	"Roadcoin Editor\n" + \
				_("Editor de niveles para el juego Roadcoin.\n") + \
				"\n " + \
				"Alberto Castillo Baquero, 2020-2021" )
		self.button_acept = tk.Button(master=self.AboutWindow, text = _("Aceptar"), image = self.img_green_tick_icon, compound = tk.LEFT, command = self.AcceptButton )


		self.canvas_logo_image.pack(side=tk.TOP, padx=2, pady=2)
		self.label_credits_text.pack(side=tk.TOP, padx=2, pady=2)
		self.button_acept.pack(side=tk.TOP, padx=2, pady=2)





	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos de la ventana de acerca de" )
		self.img_rceditorlogo_image = Image.open("images/rceditor_logo_02.png")
		self.img_rceditorlogo_photoimage = ImageTk.PhotoImage(  self.img_rceditorlogo_image  )   # PIL solution
		self.img_green_tick_icon = ImageTk.PhotoImage(Image.open("icons/green_tick-16.png"))
		# Read original image size
		self.orig_logo_image_size_width = self.img_rceditorlogo_image.width
		self.orig_logo_image_size_height = self.img_rceditorlogo_image.height


	def Draw_Logo_On_Canvas( self ):
		logging.debug( "Dibujando imagen de logo editor en ventana de acerca de" )	
		self.image_logo_canvas_object_ref = self.canvas_logo_image.create_image( 	0, \
										0, \
										image=self.img_rceditorlogo_photoimage ,\
										anchor=tk.NW)

	def AcceptButton( self ):
		self.AboutWindow.destroy()


