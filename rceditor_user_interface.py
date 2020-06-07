
import tkinter as tk
import logging
from enum import Enum
from PIL import ImageTk, Image		# Pillow
from tkinter import filedialog
from functools import partial

import rceditor_UI_operation


def do_nothing():
	x = 0


##########################################################################


class Mode(Enum):
	no_mode = 0
	general = 1
	images = 2
	rot_bg = 3
	segment = 4
	bumper = 5
	round_accel_zone = 6

mode_names = { 
	Mode.no_mode          : "Ningun modo seleccionado" , 
	Mode.general          : "Modo general" , 
	Mode.images           : "Modo imagenes" , 
	Mode.rot_bg           : "Modo fondo giratorio" , 
	Mode.segment          : "Modo segmentos" , 
	Mode.bumper           : "Modo pinball bumpers" , 
	Mode.round_accel_zone : "Modo zonas acel circ"
}

##########################################################################

class RC_editor_GUI():

	modo_actual = Mode.no_mode

	def __init__(self):
		logging.debug( "Inicializando ventana principal del editor" )
		self.window_main_editor = tk.Tk()
		self.window_main_editor.title( "RoadCoin Level Editor" )
		self.window_main_editor.minsize(600, 600)
		#self.window_main_editor.wm_iconbitmap('icon.ico')

		self.Load_UI_Icons()
		
		logging.debug( "Inicializando menu principal del editor" )
		self.menubar_mainmenu = tk.Menu( self.window_main_editor )
		self.filemenu = tk.Menu( self.menubar_mainmenu, tearoff=0)
		self.filemenu.add_command(label="Nuevo", image = self.img_new_icon, compound = tk.LEFT, command = do_nothing)
		self.filemenu.add_command(label="Abrir", image = self.img_open_icon, compound = tk.LEFT, command = self.LoadMapButton)
		self.filemenu.add_command(label="Guardar", image = self.img_save_icon, compound = tk.LEFT, command = do_nothing)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Salir", image = self.img_quit_icon, compound = tk.LEFT, command = self.window_main_editor.quit)
		self.menubar_mainmenu.add_cascade(label="Archivo", menu = self.filemenu)
		self.helpmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.helpmenu.add_command(label="Help Index", command = do_nothing)
		self.helpmenu.add_command(label="About...", command = do_nothing)
		self.menubar_mainmenu.add_cascade(label="Ayuda", menu=self.helpmenu)
		self.window_main_editor.config( menu = self.menubar_mainmenu )
		# Nota: añadir imagenes a los menus con image=self._img4, compound='left',...etc

		logging.debug( "Inicializando barra de herramientas superior" )
		self.frame_upper_mode_toolbar = tk.Frame( self.window_main_editor )
		self.button_gen_mode = tk.Button(self.frame_upper_mode_toolbar, text="Gen", width=6, command = partial( self.Reconf_UI_To_Mode, Mode.general ) )
		self.button_img_mode = tk.Button(self.frame_upper_mode_toolbar, text="Img", image = self.img_img_icon, compound = tk.LEFT, command = partial( self.Reconf_UI_To_Mode, Mode.images ) )
		self.button_rotbg_mode = tk.Button(self.frame_upper_mode_toolbar, text="Rotbg", width=6, command = partial( self.Reconf_UI_To_Mode, Mode.rot_bg ) )
		self.button_segm_mode = tk.Button(self.frame_upper_mode_toolbar, text="Segm", image = self.img_segm_icon, compound = tk.LEFT, command = partial( self.Reconf_UI_To_Mode, Mode.segment ) )
		self.button_bump_mode = tk.Button(self.frame_upper_mode_toolbar, text="Bump", image = self.img_bumper_icon, compound = tk.LEFT, command = partial( self.Reconf_UI_To_Mode, Mode.bumper ) )
		self.button_raccz_mode = tk.Button(self.frame_upper_mode_toolbar, text="Raccz", image = self.img_raccz_icon, compound = tk.LEFT, command = partial( self.Reconf_UI_To_Mode, Mode.round_accel_zone ) )
		self.buttons_mode_list = [ self.button_gen_mode, self.button_img_mode, self.button_rotbg_mode, self.button_segm_mode, self.button_bump_mode, self.button_raccz_mode ]
		for obj in self.buttons_mode_list:
			obj.pack(side=tk.LEFT, padx=2, pady=2)
		self.label_mode = tk.Label( master=self.frame_upper_mode_toolbar, text = mode_names.get(Mode.no_mode) )
		self.label_mode.pack(side=tk.LEFT, padx=2, pady=2)
		self.frame_upper_mode_toolbar.pack(side=tk.TOP, fill=tk.X)

		# Save original button color in order to restore it later
		self.orig_button_bg_color = self.button_gen_mode.cget("background")

		logging.debug( "Inicializando frame central" )
		self.central_frame = tk.Frame( master = self.window_main_editor)
		self.central_frame.columnconfigure( 0, weight=0, minsize=100)		# For frame_left_toolbar
		self.central_frame.columnconfigure( 1, weight=1, minsize=100)		# For frame_mapview
		self.central_frame.columnconfigure( 2, weight=0, minsize=100)		# For frame_properties
		self.central_frame.rowconfigure( 0, weight=1, minsize=500)
		self.central_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.frame_left_toolbar = tk.Frame( master = self.central_frame )
		self.frame_left_toolbar.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.frame_mapview = tk.Frame( master = self.central_frame, relief=tk.GROOVE, borderwidth=20 )
		self.frame_mapview.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.frame_properties = tk.Frame( master = self.central_frame )
		self.frame_properties.grid(row=0, column=2,  padx=2, pady=2, sticky="nsew" )

		# Aqui faltan muchas cosas.....
		logging.debug( "Inicializando canvas para dibujar el mapa" )
		self.canvas_mapview = tk.Canvas( master = self.frame_mapview )
		self.canvas_mapview.pack(fill=tk.BOTH , expand=True )


		logging.debug( "Inicializando barra de estado" )
		#self.window_statusbar = StatusBar( self.window_main_editor )
		#self.window_statusbar.set("%s", "Holaaaaaaaa")
		#self.window_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
		self.window_statusbar = StatusBar_2Fields( self.window_main_editor )
		self.window_statusbar.set_field_1("%s", "Holaaaaaaaa")
		self.window_statusbar.set_field_2("%s", "CoordRaton")		
		self.window_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

		logging.debug( "Creando botones de herramientas de cada modo" )	
		self.button_gen1 = tk.Button( master = self.frame_left_toolbar, text="Gen1", width=6, command = do_nothing)
		self.button_gen2 = tk.Button( master = self.frame_left_toolbar, text="Gen2", width=6, command = do_nothing)
		self.button_gen3 = tk.Button( master = self.frame_left_toolbar, text="Gen3", width=6, command = do_nothing)
		self.button_gen4 = tk.Button( master = self.frame_left_toolbar, text="Gen4", width=6, command = do_nothing)
		self.buttons_gen_list = [ self.button_gen1, self.button_gen2, self.button_gen3, self.button_gen4 ]
		self.button_img1 = tk.Button( master = self.frame_left_toolbar, text="Img1", width=6, command = do_nothing)
		self.button_img2 = tk.Button( master = self.frame_left_toolbar, text="Img2", width=6, command = do_nothing)
		self.button_img3 = tk.Button( master = self.frame_left_toolbar, text="Img3", width=6, command = do_nothing)
		self.button_img4 = tk.Button( master = self.frame_left_toolbar, text="Img4", width=6, command = do_nothing)
		self.button_img5 = tk.Button( master = self.frame_left_toolbar, text="Img5", width=6, command = do_nothing)
		self.buttons_img_list = [ self.button_img1, self.button_img2, self.button_img3, self.button_img4, self.button_img5 ]
		self.button_rotbg1 = tk.Button( master = self.frame_left_toolbar, text="Rotbg1", width=6, command = do_nothing)
		self.button_rotbg2 = tk.Button( master = self.frame_left_toolbar, text="Rotbg2", width=6, command = do_nothing)
		self.button_rotbg3 = tk.Button( master = self.frame_left_toolbar, text="Rotbg3", width=6, command = do_nothing)
		self.buttons_rotbg_list = [ self.button_rotbg1, self.button_rotbg2, self.button_rotbg3 ]
		self.button_segm1 = tk.Button( master = self.frame_left_toolbar, text="Segm1", width=6, command = do_nothing)
		self.button_segm2 = tk.Button( master = self.frame_left_toolbar, text="Segm2", width=6, command = do_nothing)
		self.button_segm3 = tk.Button( master = self.frame_left_toolbar, text="Segm3", width=6, command = do_nothing)
		self.button_segm4 = tk.Button( master = self.frame_left_toolbar, text="Segm4", width=6, command = do_nothing)
		self.button_segm5 = tk.Button( master = self.frame_left_toolbar, text="Segm5", width=6, command = do_nothing)
		self.button_segm6 = tk.Button( master = self.frame_left_toolbar, text="Segm6", width=6, command = do_nothing)
		self.buttons_segm_list = [ self.button_segm1, self.button_segm2, self.button_segm3, self.button_segm4, self.button_segm5, self.button_segm6 ]
		self.button_bump1 = tk.Button( master = self.frame_left_toolbar, text="Bump1", width=6, command = do_nothing)
		self.button_bump2 = tk.Button( master = self.frame_left_toolbar, text="Bump2", width=6, command = do_nothing)
		self.button_bump3 = tk.Button( master = self.frame_left_toolbar, text="Bump3", width=6, command = do_nothing)
		self.buttons_bump_list = [ self.button_bump1, self.button_bump2, self.button_bump3 ]
		self.button_raccz1 = tk.Button( master = self.frame_left_toolbar, text="Raccz1", width=6, command = do_nothing)
		self.button_raccz2 = tk.Button( master = self.frame_left_toolbar, text="Raccz2", width=6, command = do_nothing)
		self.button_raccz3 = tk.Button( master = self.frame_left_toolbar, text="Raccz3", width=6, command = do_nothing)
		self.button_raccz4 = tk.Button( master = self.frame_left_toolbar, text="Raccz4", width=6, command = do_nothing)
		self.buttons_raccz_list = [ self.button_raccz1, self.button_raccz2, self.button_raccz3, self.button_raccz4 ]

		logging.debug( "Configurando gestores de eventos" )			
		self.Set_UI_Event_Handlers()


	def MainWindowLoop(self):
		logging.debug("Iniciando bucle principal TK para window_main_editor")
		self.window_main_editor.mainloop()


	def Reconf_UI_To_Mode(self, new_mode):
		logging.debug("Reconfigurando la ventana al " + mode_names.get(new_mode)  )
		self.UnPack_LeftToolbar_Buttons( self.modo_actual )
		self.Pack_LeftToolbar_Buttons( new_mode )
		self.ChangeModeUpperToolbar( new_mode )
		self.modo_actual = new_mode


	def UnPack_LeftToolbar_Buttons(self, old_mode):
		if old_mode == Mode.general:
			for obj in self.buttons_gen_list:
				obj.pack_forget()
		elif old_mode == Mode.images:
			for obj in self.buttons_img_list:
				obj.pack_forget()
		elif old_mode == Mode.rot_bg:
			for obj in self.buttons_rotbg_list:
				obj.pack_forget()
		elif old_mode == Mode.segment:
			for obj in self.buttons_segm_list:
				obj.pack_forget()
		elif old_mode == Mode.bumper:
			for obj in self.buttons_bump_list:
				obj.pack_forget()
		elif old_mode == Mode.round_accel_zone:
			for obj in self.buttons_raccz_list:
				obj.pack_forget()

	def Pack_LeftToolbar_Buttons(self, new_mode):
		if new_mode == Mode.general:
			for obj in self.buttons_gen_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)	
		elif new_mode == Mode.images:
			for obj in self.buttons_img_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.rot_bg:
			for obj in self.buttons_rotbg_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.segment:
			for obj in self.buttons_segm_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.bumper:
			for obj in self.buttons_bump_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.round_accel_zone:
			for obj in self.buttons_raccz_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)

	def UnPack_Properties(self, old_mode):
		pass

	def Pack_Properties(self, new_mode):
		pass

	def ChangeModeUpperToolbar(self , new_mode ):
		for obj in self.buttons_mode_list:
			obj.configure(bg = self.orig_button_bg_color )
		if new_mode == Mode.general:
			self.button_gen_mode.configure(bg = "green")
		elif new_mode == Mode.images:
			self.button_img_mode.configure(bg = "green")
		elif new_mode == Mode.rot_bg:
			self.button_rotbg_mode.configure(bg = "green")
		elif new_mode == Mode.segment:
			self.button_segm_mode.configure(bg = "green")
		elif new_mode == Mode.bumper:
			self.button_bump_mode.configure(bg = "green")
		elif new_mode == Mode.round_accel_zone:
			self.button_raccz_mode.configure(bg = "green")
		self.label_mode.configure(text=mode_names.get(new_mode))


	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos del editor" )
		#self.img_quit_icon = tk.PhotoImage(file = r"icons/quit-512.png") 	# Tk solution
		self.img_quit_icon = ImageTk.PhotoImage(Image.open("icons/quit-16.png"))  # PIL solution
		self.img_save_icon = ImageTk.PhotoImage(Image.open("icons/fd-16.png"))
		self.img_open_icon = ImageTk.PhotoImage(Image.open("icons/open_folder-16.png"))
		self.img_new_icon = ImageTk.PhotoImage(Image.open("icons/file-16.png"))

		self.img_segm_icon = ImageTk.PhotoImage(Image.open("icons/segm-16.png"))
		self.img_bumper_icon = ImageTk.PhotoImage(Image.open("icons/bumper-16.png"))
		self.img_img_icon = ImageTk.PhotoImage(Image.open("icons/img-16.png"))
		self.img_raccz_icon = ImageTk.PhotoImage(Image.open("icons/raccz-16.png"))

	def Set_UI_Event_Handlers(self):
		self.canvas_mapview.bind('<Motion>', self.mapview_mouse_motion_event_handler )
	
	#############################################################################
	# Event handlers
	def mapview_mouse_motion_event_handler(self, event):
		# When mouse moves over canvas, get the mouse coordinates
		x, y = event.x, event.y
		# print('{}, {}'.format(x, y))
		self.window_statusbar.set_field_2( "%s", "( " + str(x) + " , " + str(y) + " )" )


	##############################################################################

	def LoadMapButton(self):
		self.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
		# aqui faltan muchas cosas mas ....





###########################################################################

class StatusBar(tk.Frame):

	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label.pack(fill=tk.X)

	def set(self, format, *args):
		self.label.config(text=format % args)
		self.label.update_idletasks()

	def clear(self):
		self.label.config(text="")
		self.label.update_idletasks()

###########################################################################

class StatusBar_2Fields(tk.Frame):

	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.columnconfigure( 0, weight=1, minsize=500)
		self.columnconfigure( 1, weight=0, minsize=100)
		self.label_field_1 = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label_field_2 = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label_field_1.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.label_field_2.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )

	def set_field_1(self, format, *args):
		self.label_field_1.config(text=format % args)
		self.label_field_1.update_idletasks()

	def set_field_2(self, format, *args):
		self.label_field_2.config(text=format % args)
		self.label_field_2.update_idletasks()

	def clear_field_1(self):
		self.label_field_1.config(text="")
		self.label_field_1.update_idletasks()

	def clear_field_2(self):
		self.label_field_2.config(text="")
		self.label_field_2.update_idletasks()


		
