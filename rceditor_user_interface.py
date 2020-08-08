
import tkinter as tk
import logging
from enum import Enum
from PIL import ImageTk, Image		# Pillow
from tkinter import filedialog
from tkinter import messagebox
from functools import partial
import sys

#import rceditor_UI_operation
import rceditor_maps
import rceditor_mapview
import rceditor_preferences
import rceditor_custom_widgets


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

class Segment_SubMode(Enum):
	no_mode = 0
	add = 1
	edit = 2
	delete = 3

segment_submode_names = {
	Segment_SubMode.no_mode		: "Ningun submodo seleccionado",
	Segment_SubMode.add		: "Submodo añadir",
	Segment_SubMode.edit		: "Submodo editar",
	Segment_SubMode.delete		: "Submodo eliminar"
}

##########################################################################

class RC_editor_GUI():

	current_mode = Mode.no_mode
	current_segment_submode = Segment_SubMode.no_mode
	map_loaded = False
	loaded_map_filename = None


	def __init__(self):
		logging.debug( "Cargando fichero de preferencias" )
		self.preferences = rceditor_preferences.Preferences()
		self.preferences.LoadPreferences()

		logging.debug( "Inicializando ventana principal del editor" )
		self.window_main_editor = tk.Tk()
		self.window_main_editor.title( "RoadCoin Level Editor" )
		self.window_main_editor.minsize(600, 600)
		#self.window_main_editor.wm_iconbitmap('icon.ico')

		self.Load_UI_Icons()
		
		logging.debug( "Inicializando menu principal del editor" )
		self.menubar_mainmenu = tk.Menu( self.window_main_editor )
		self.filemenu = tk.Menu( self.menubar_mainmenu, tearoff=0)
		self.filemenu.add_command(label="Nuevo", image = self.img_new_icon, compound = tk.LEFT, command = do_nothing )
		self.filemenu.add_command(label="Abrir", image = self.img_open_icon, compound = tk.LEFT, command = self.LoadMapButton )
		self.filemenu.add_command(label="Guardar", image = self.img_save_icon, compound = tk.LEFT, command = do_nothing )
		self.filemenu.add_command(label="Cerrar", image = self.img_close_icon, compound = tk.LEFT, command=self.CloseMapButton )
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Salir", image = self.img_quit_icon, compound = tk.LEFT, command = self.window_main_editor.quit)
		self.menubar_mainmenu.add_cascade(label="Archivo", menu = self.filemenu)
		self.editmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.editmenu.add_command(label="Deshacer", command = do_nothing)
		self.editmenu.add_command(label="Rehacer", command = do_nothing)
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Preferencias...", command = self.ShowPreferencesWindowButton )
		self.menubar_mainmenu.add_cascade(label="Editar", menu=self.editmenu)
		self.viewmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.viewmenu.add_command(label="Redibujar todo", image=self.img_reload_icon, compound = tk.LEFT, command = self.RedrawAllButton )
		self.viewmenu.add_separator()
		self.viewmenu.add_command(label="Volver a (0,0)", image=self.img_origin_icon, compound = tk.LEFT, command = self.GoTo_Origin )
		self.menubar_mainmenu.add_cascade(label="Vista", menu=self.viewmenu)
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
		self.frame_mapview = tk.Frame( master = self.central_frame, relief=tk.GROOVE, borderwidth=5 )
		self.frame_mapview.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.frame_properties = tk.Frame( master = self.central_frame )
		self.frame_properties.grid(row=0, column=2,  padx=2, pady=2, sticky="nsew" )

		# Aqui faltan muchas cosas.....
		logging.debug( "Inicializando canvas para dibujar el mapa" )
		# self.canvas_mapview = tk.Canvas( master = self.frame_mapview )				# Without scrollbars
		self.canvas_mapview = rceditor_mapview.Canvas_WithScrollbars( master = self.frame_mapview )	# With scrollbars
		self.canvas_mapview.pack(fill=tk.BOTH , expand=True )


		logging.debug( "Inicializando barra de estado" )
		#self.window_statusbar = StatusBar( self.window_main_editor )
		#self.window_statusbar.set("%s", "Holaaaaaaaa")
		#self.window_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
		self.window_statusbar = rceditor_custom_widgets.StatusBar_MultiFields( self.window_main_editor )
		self.window_statusbar.set_field_1("%s", "Bienvenido al editor de niveles de Roadcoin")
		self.window_statusbar.set_field_2("%s", "CoordRaton")	
		self.window_statusbar.set_field_3("%s", "Zoom: 100%")	
		self.window_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

		logging.debug( "Creando botones de herramientas de cada modo" )	
		# General mode buttons
		self.button_gen1 = tk.Button( master = self.frame_left_toolbar, text="Gen1", width=6, command = do_nothing)
		self.button_gen2 = tk.Button( master = self.frame_left_toolbar, text="Gen2", width=6, command = do_nothing)
		self.button_gen3 = tk.Button( master = self.frame_left_toolbar, text="Gen3", width=6, command = do_nothing)
		self.button_gen4 = tk.Button( master = self.frame_left_toolbar, text="Gen4", width=6, command = do_nothing)
		self.buttons_gen_list = [ self.button_gen1, self.button_gen2, self.button_gen3, self.button_gen4 ]
		# Image mode buttons
		self.button_img1 = tk.Button( master = self.frame_left_toolbar, text="Img1", width=6, command = do_nothing)
		self.button_img2 = tk.Button( master = self.frame_left_toolbar, text="Img2", width=6, command = do_nothing)
		self.button_img3 = tk.Button( master = self.frame_left_toolbar, text="Img3", width=6, command = do_nothing)
		self.button_img4 = tk.Button( master = self.frame_left_toolbar, text="Img4", width=6, command = do_nothing)
		self.button_img5 = tk.Button( master = self.frame_left_toolbar, text="Img5", width=6, command = do_nothing)
		self.buttons_img_list = [ self.button_img1, self.button_img2, self.button_img3, self.button_img4, self.button_img5 ]
		# Rotating background mode buttons
		self.button_rotbg1 = tk.Button( master = self.frame_left_toolbar, text="Rotbg1", width=6, command = do_nothing)
		self.button_rotbg2 = tk.Button( master = self.frame_left_toolbar, text="Rotbg2", width=6, command = do_nothing)
		self.button_rotbg3 = tk.Button( master = self.frame_left_toolbar, text="Rotbg3", width=6, command = do_nothing)
		self.buttons_rotbg_list = [ self.button_rotbg1, self.button_rotbg2, self.button_rotbg3 ]
		# Segment mode buttons
		self.button_new_segm = tk.Button( master = self.frame_left_toolbar, text="Nuevo", image=self.img_new_segm_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_SegmentSubMode, Segment_SubMode.add) )
		self.button_edit_segm = tk.Button( master = self.frame_left_toolbar, text="Editar", image=self.img_edit_segm_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_SegmentSubMode, Segment_SubMode.edit ) )
		self.button_del_segm = tk.Button( master = self.frame_left_toolbar, text="Eliminar", image=self.img_del_segm_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_SegmentSubMode, Segment_SubMode.delete ) )
		self.button_segm4 = tk.Button( master = self.frame_left_toolbar, text="Segm4", width=6, command = do_nothing)
		self.button_segm5 = tk.Button( master = self.frame_left_toolbar, text="Segm5", width=6, command = do_nothing)
		self.button_segm6 = tk.Button( master = self.frame_left_toolbar, text="Segm6", width=6, command = do_nothing)
		self.buttons_segm_list = [ self.button_new_segm, self.button_edit_segm, self.button_del_segm, self.button_segm4, self.button_segm5, self.button_segm6 ]
		# Bumpers mode buttons
		self.button_bump1 = tk.Button( master = self.frame_left_toolbar, text="Bump1", width=6, command = do_nothing)
		self.button_bump2 = tk.Button( master = self.frame_left_toolbar, text="Bump2", width=6, command = do_nothing)
		self.button_bump3 = tk.Button( master = self.frame_left_toolbar, text="Bump3", width=6, command = do_nothing)
		self.buttons_bump_list = [ self.button_bump1, self.button_bump2, self.button_bump3 ]
		# RACCZ mode buttons
		self.button_raccz1 = tk.Button( master = self.frame_left_toolbar, text="Raccz1", width=6, command = do_nothing)
		self.button_raccz2 = tk.Button( master = self.frame_left_toolbar, text="Raccz2", width=6, command = do_nothing)
		self.button_raccz3 = tk.Button( master = self.frame_left_toolbar, text="Raccz3", width=6, command = do_nothing)
		self.button_raccz4 = tk.Button( master = self.frame_left_toolbar, text="Raccz4", width=6, command = do_nothing)
		self.buttons_raccz_list = [ self.button_raccz1, self.button_raccz2, self.button_raccz3, self.button_raccz4 ]


		logging.debug( "Creando widgets del panel de propiedades para cada modo " )
		# General mode properties widgets
		self.property_gen1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 1", callback=do_nothing )
		self.property_gen2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 2", callback=do_nothing )
		self.property_gen3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 3", callback=do_nothing )
		self.properties_gen_list = [ self.property_gen1, self.property_gen2, self.property_gen3 ]
		# Image mode properties widgets
		self.property_img1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 1", callback=do_nothing )
		self.property_img2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 2", callback=do_nothing )
		self.property_img3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 3", callback=do_nothing )
		self.properties_img_list = [ self.property_img1, self.property_img2, self.property_img3 ]
		# Rotating background mode properties widgets
		self.property_rotbg1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 1", callback=do_nothing )
		self.property_rotbg2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 2", callback=do_nothing )
		self.property_rotbg3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 3", callback=do_nothing )
		self.properties_rotbg_list = [ self.property_rotbg1, self.property_rotbg2, self.property_rotbg3 ]
		# Segment mode properties widgets
		self.property_segm_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Numero segmento:", callback=do_nothing )
		self.property_segm_start_label = tk.Label(master=self.frame_properties,text="Start:")
		self.property_segm_start_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", callback=do_nothing )
		self.property_segm_start_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", callback=do_nothing )
		self.property_segm_end_label = tk.Label(master=self.frame_properties,text="End:")
		self.property_segm_end_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", callback=do_nothing )
		self.property_segm_end_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", callback=do_nothing )
		self.property_segm_type_label = tk.Label(master=self.frame_properties, text="Tipo segmento:")
		self.property_segm_type_variable = tk.StringVar()
		self.property_segm_type_choices = [ rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.wall), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.goal), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.death), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_L), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_R)  ]
		self.property_segm_type = tk.OptionMenu( self.frame_properties, self.property_segm_type_variable, *self.property_segm_type_choices )
		self.property_segm_invis = tk.Checkbutton(master=self.frame_properties, text="Invisible")
		self.properties_segm_list = [ self.property_segm_number, self.property_segm_start_label, self.property_segm_start_x, self.property_segm_start_y, self.property_segm_end_label, self.property_segm_end_x, self.property_segm_end_y, self.property_segm_type_label, self.property_segm_type, self.property_segm_type, self.property_segm_invis ]
		# Bumpers mode properties widgets
		self.property_bump1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="bump 1", callback=do_nothing )
		self.property_bump2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="bump 2", callback=do_nothing )
		self.property_bump3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="bump 3", callback=do_nothing )
		self.properties_bump_list = [ self.property_bump1, self.property_bump2, self.property_bump3 ]
		# RACCZ mode properties widgets
		self.property_raccz1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="raccz 1", callback=do_nothing )
		self.property_raccz2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="raccz 2", callback=do_nothing )
		self.property_raccz3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="raccz 3", callback=do_nothing )
		self.properties_raccz_list = [ self.property_raccz1, self.property_raccz2, self.property_raccz3 ]


		self.map_loaded = False
		self.DisableMenuItems_MapUnloaded()

		logging.debug( "Configurando gestores de eventos" )			
		self.Set_UI_Event_Handlers()		# Desactivado temporalmente



	def MainWindowLoop(self):
		logging.debug("Iniciando bucle principal TK para window_main_editor")
		self.window_main_editor.mainloop()


	def Reconf_UI_To_Mode(self, new_mode):
		logging.debug("Reconfigurando la ventana al " + mode_names.get(new_mode)  )
		self.UnPack_LeftToolbar_Buttons( self.current_mode )
		self.Pack_LeftToolbar_Buttons( new_mode )
		self.UnPack_Properties( self.current_mode )
		self.Pack_Properties( new_mode )
		self.ChangeModeUpperToolbar( new_mode )
		self.current_mode = new_mode


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
		if old_mode == Mode.general:
			for obj in self.properties_gen_list:
				obj.pack_forget()
		elif old_mode == Mode.images:
			for obj in self.properties_img_list:
				obj.pack_forget()
		elif old_mode == Mode.rot_bg:
			for obj in self.properties_rotbg_list:
				obj.pack_forget()
		elif old_mode == Mode.segment:
			for obj in self.properties_segm_list:
				obj.pack_forget()
		elif old_mode == Mode.bumper:
			for obj in self.properties_bump_list:
				obj.pack_forget()
		elif old_mode == Mode.round_accel_zone:
			for obj in self.properties_raccz_list:
				obj.pack_forget()


	def Pack_Properties(self, new_mode):
		if new_mode == Mode.general:
			for obj in self.properties_gen_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)	
		elif new_mode == Mode.images:
			for obj in self.properties_img_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.rot_bg:
			for obj in self.properties_rotbg_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.segment:
			for obj in self.properties_segm_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.bumper:
			for obj in self.properties_bump_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)
		elif new_mode == Mode.round_accel_zone:
			for obj in self.properties_raccz_list:
				obj.pack(side=tk.TOP, padx=2, pady=2)


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


	def Reconf_UI_To_SegmentSubMode(self, new_segment_submode):
		# Restore colors of old mode button
		if self.current_segment_submode == Segment_SubMode.add:
			self.button_new_segm.configure( bg = self.orig_button_bg_color )
		elif self.current_segment_submode == Segment_SubMode.edit:
			self.button_edit_segm.configure( bg = self.orig_button_bg_color )
		elif self.current_segment_submode == Segment_SubMode.delete:
			self.button_del_segm.configure( bg = self.orig_button_bg_color )

		if new_segment_submode == self.current_segment_submode:
			logging.debug( "Ningun submodo segmentos seleccionado")
			
			self.current_segment_submode = Segment_SubMode.no_mode
			return
		else:
			logging.debug( "Activando submodo segmentos " + segment_submode_names.get(new_segment_submode) )
			self.current_segment_submode = new_segment_submode
			# Draw color of new mode button
			if new_segment_submode == Segment_SubMode.add:
				self.button_new_segm.configure( bg = "green" )
			elif new_segment_submode == Segment_SubMode.edit:
				self.button_edit_segm.configure( bg = "green" )
			elif new_segment_submode == Segment_SubMode.delete:
				self.button_del_segm.configure( bg = "green" )




	def EnableMenuItems_MapLoaded( self ):
		self.filemenu.entryconfig("Cerrar", state="normal")
		self.editmenu.entryconfig("Deshacer", state="normal")
		self.editmenu.entryconfig("Rehacer", state="normal")
		self.viewmenu.entryconfig("Redibujar todo", state="normal")
		self.viewmenu.entryconfig("Volver a (0,0)", state="normal")

	def DisableMenuItems_MapUnloaded( self ):
		self.filemenu.entryconfig("Cerrar", state="disabled")
		self.editmenu.entryconfig("Deshacer", state="disabled")
		self.editmenu.entryconfig("Rehacer", state="disabled")
		self.viewmenu.entryconfig("Redibujar todo", state="disabled")
		self.viewmenu.entryconfig("Volver a (0,0)", state="disabled")

	def Load_UI_Icons(self):
		logging.debug( "Cargando iconos del editor" )
		#self.img_quit_icon = tk.PhotoImage(file = r"icons/quit-512.png") 	# Tk solution
		self.img_quit_icon = ImageTk.PhotoImage(Image.open("icons/quit-16.png"))  # PIL solution
		self.img_save_icon = ImageTk.PhotoImage(Image.open("icons/fd-16.png"))
		self.img_open_icon = ImageTk.PhotoImage(Image.open("icons/open_folder-16.png"))
		self.img_new_icon = ImageTk.PhotoImage(Image.open("icons/file-16.png"))
		self.img_close_icon = ImageTk.PhotoImage(Image.open("icons/x_icon-16.png"))
		self.img_reload_icon = ImageTk.PhotoImage(Image.open("icons/reload-16.png"))
		self.img_origin_icon = ImageTk.PhotoImage(Image.open("icons/origin-16.png"))

		self.img_segm_icon = ImageTk.PhotoImage(Image.open("icons/segm-16.png"))
		self.img_bumper_icon = ImageTk.PhotoImage(Image.open("icons/bumper-16.png"))
		self.img_img_icon = ImageTk.PhotoImage(Image.open("icons/img-16.png"))
		self.img_raccz_icon = ImageTk.PhotoImage(Image.open("icons/raccz-16.png"))

		self.img_new_segm_icon = ImageTk.PhotoImage(Image.open("icons/new_segm-16.png"))
		self.img_edit_segm_icon = ImageTk.PhotoImage(Image.open("icons/edit_segm-16.png"))
		self.img_del_segm_icon = ImageTk.PhotoImage(Image.open("icons/del_segm-16.png"))

	def Set_UI_Event_Handlers(self):
		# self.canvas_mapview.bind('<Motion>', self.mapview_mouse_motion_event_handler )			# For canvas without scrollbars
		self.canvas_mapview.viewer.bind('<Motion>', self.mapview_mouse_motion_event_handler )			# For canvas with scrollbars
		self.canvas_mapview.viewer.bind('<Enter>', self.bind_mapview_to_mouse_buttons_and_wheel )
		self.canvas_mapview.viewer.bind('<Leave>', self.unbind_mapview_to_mouse_buttons_and_wheel)

	#############################################################################
	# Event handlers
	def mapview_mouse_motion_event_handler(self, event):
		if self.map_loaded == True:
			# When mouse moves over canvas, get the mouse coordinates
			# x, y = event.x, event.y	# Does not take scrolling into account
			canvas_x = self.canvas_mapview.viewer.canvasx(event.x)
			canvas_y = self.canvas_mapview.viewer.canvasy(event.y)
			map_x = int(canvas_x / self.canvas_mapview.zoomlevel)
			map_y = int(canvas_y / self.canvas_mapview.zoomlevel)
			# print('{}, {}'.format(x, y))
			self.window_statusbar.set_field_2( "%s", "( " + str(map_x) + " , " + str(map_y) + " )" )

	def bind_mapview_to_mouse_buttons_and_wheel( self, event ):
		logging.debug("Raton entra en zona de visor de mapa")
		if sys.platform.startswith('win'):
			logging.debug("Nota: version Windows")
			# with Windows OS
			self.canvas_mapview.viewer.bind("<Button>", self.mouse_button_event_handler_windows)
			self.canvas_mapview.viewer.bind_all("<MouseWheel>", self.mapview_vertical_mousewheel_event_handler_windows)
			self.canvas_mapview.viewer.bind_all("<Control-MouseWheel>", self.mapview_ctrl_vertical_mousewheel_event_handler)
			# (TODO) Horizontal MouseWheel for Windows is yet to be programmed
		elif 'linux' in sys.platform:
			logging.debug("Nota: version GNU-Linux")
			# with GNU/Linux OS + X11
			self.canvas_mapview.viewer.bind("<Button>", self.mouse_button_event_handler_linux)
			#self.canvas_mapview.viewer.bind("<Button-4>", self.mapview_vertical_mousewheel_event_handler)
			#self.canvas_mapview.viewer.bind("<Button-5>", self.mapview_vertical_mousewheel_event_handler)
			#self.canvas_mapview.viewer.bind("<Button-6>", self.mapview_horizontal_mousewheel_event_handler)	# Does not work
			#self.canvas_mapview.viewer.bind("<Button-7>", self.mapview_horizontal_mousewheel_event_handler)	# Does not work
			self.canvas_mapview.viewer.bind("<Control-Button-4>", self.mapview_ctrl_vertical_mousewheel_event_handler)
			self.canvas_mapview.viewer.bind("<Control-Button-5>", self.mapview_ctrl_vertical_mousewheel_event_handler)



	def unbind_mapview_to_mouse_buttons_and_wheel( self, event ):
		logging.debug("Raton sale de zona de visor de mapa")
		if sys.platform.startswith('win'):
			logging.debug("Nota: version Windows")
			# with Windows OS
			self.canvas_mapview.viewer.unbind_all("<Button>")
			self.canvas_mapview.viewer.unbind_all("<MouseWheel>")
			self.canvas_mapview.viewer.unbind_all("<Control-MouseWheel>")
		elif 'linux' in sys.platform:
			logging.debug("Nota: version GNU-Linux")
			# with GNU/Linux OS + X11
			self.canvas_mapview.viewer.unbind_all("<Button>")
			#self.canvas_mapview.viewer.unbind_all("<Button-4>")
			#self.canvas_mapview.viewer.unbind_all("<Button-5>")
			#self.canvas_mapview.viewer.unbind_all("<Button-6>")
			#self.canvas_mapview.viewer.unbind_all("<Button-7>")
			self.canvas_mapview.viewer.unbind_all("<Control-Button-4>")
			self.canvas_mapview.viewer.unbind_all("<Control-Button-5>")


	def mouse_button_event_handler_windows( self, event ):
		if self.map_loaded == True:
			# For al OS
			self.mouse_button_event_handler_OS_common( event )


	def mouse_button_event_handler_linux( self, event ):
		if self.map_loaded == True:
			# with GNU/Linux OS + X11
			if event.num == 5:
				logging.debug("Aplicando desplazamiento al visor de mapa en dirección Y+ (version GNU/Linux)")
				self.canvas_mapview.viewer.yview_scroll( 1 , "units" )
			if event.num == 4:
				logging.debug("Aplicando desplazamiento al visor de mapa en dirección Y- (version GNU/Linux)")
				self.canvas_mapview.viewer.yview_scroll( -1 , "units" )
			if event.num == 6:
				logging.debug("Aplicando desplazamiento al visor de mapa en dirección X- (version GNU/Linux)")
				self.canvas_mapview.viewer.xview_scroll( -1 , "units" )
			if event.num == 7:
				logging.debug("Aplicando desplazamiento al visor de mapa en dirección X+ (version GNU/Linux)")
				self.canvas_mapview.viewer.xview_scroll( 1 , "units" )
			# For al OS
			self.mouse_button_event_handler_OS_common( event )


	def mouse_button_event_handler_OS_common( self, event ):
		if self.map_loaded == True:
			canvas_x = self.canvas_mapview.viewer.canvasx(event.x)
			canvas_y = self.canvas_mapview.viewer.canvasy(event.y)
			map_x = int(canvas_x / self.canvas_mapview.zoomlevel)
			map_y = int(canvas_y / self.canvas_mapview.zoomlevel)
			logging.debug("Pulsado boton " + str( event.num ) + " en x=" + str(map_x) + ", y=" + str(map_y) +", modo = " + mode_names.get( self.current_mode ) )
			if event.num == 1:	# Left mouse button clicked
				if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.edit:
					segment_found = None
					canvas_object_found = self.canvas_mapview.viewer.find_closest(canvas_x, canvas_y)[0]
					logging.debug("Encontrado objeto con identificador " + str( canvas_object_found ) + " en el lienzo" )
					if canvas_object_found in self.canvas_mapview.segment_lines_dict:
						segment_found = self.canvas_mapview.segment_lines_dict.get(canvas_object_found)
						logging.debug("Encontrado segmento " + str( segment_found ) )
					elif canvas_object_found in self.canvas_mapview.segment_num_texts_dict:
						segment_found = self.canvas_mapview.segment_num_texts_dict.get(canvas_object_found)
						logging.debug("Encontrado texto numero segmento " + str( segment_found ) )
					else:
						segment_found = None	# We found something that was not a line segment
						logging.debug("No se ha encontrado nada.")
					if segment_found is not None:
						self.canvas_mapview.UnHighlight_Segments()
						self.canvas_mapview.Highlight_Segments( [ segment_found ] )		# Type cast into list
						self.Update_Selected_Segment_Properties( segment_found )
				# elif bla bla bla, other modes
				# elif bla bla bla, other modes
			if event.num == 2:	# Middle mouse button clicked
				pass
			if event.num == 3:	# Right mouse button clicked
				pass


	def mapview_vertical_mousewheel_event_handler_windows(self, event):
		if self.map_loaded == True:
			# with Windows OS
			logging.debug("Aplicando desplazamiento al visor de mapa en dirección Y (version windows)")
			self.canvas_mapview.viewer.yview_scroll( int(-1*(event.delta/120)), "units")



	def mapview_horizontal_mousewheel_event_handler_windows(self, event):
		if self.map_loaded == True:
			logging.debug("Aplicando desplazamiento al visor de mapa en dirección X (version windows)")
			# with Windows OS
			self.canvas_mapview.viewer.xview_scroll( int(-1*(event.delta/120)), "units")	# (TODO) Horizontal MouseWheel for Windows is yet to be programmed


	def mapview_ctrl_vertical_mousewheel_event_handler(self, event):
		if self.map_loaded == True:
			logging.debug("Aplicando zoom al visor de mapa")
			if sys.platform.startswith('win'):
				# with Windows OS
				self.ChangeZoomLevel( zoom_increment= event.delta/120 )
			elif 'linux' in sys.platform:
				# with GNU/Linux OS + X11
				if event.num == 5:
					#self.canvas_mapview.zoomlevel -= 0.1
					self.ChangeZoomLevel( zoom_increment= -0.1)
				if event.num == 4:
					#self.canvas_mapview.zoomlevel += 0.1
					self.ChangeZoomLevel( zoom_increment= +0.1)

	##############################################################################

	def LoadMapButton(self):
		if self.map_loaded == True:
			answer = tk.messagebox.askyesnocancel("Abrir otro mapa", "¿Desea abrir otro mapa?\nSe perderán las modificaciones realizadas en el mapa actual")
			logging.debug( "Pregunta abrir otro mapa, el usuario ha respondido answer = " + str(answer) )
			if (answer is None) or (answer == False) :
				return	# Do nothing

		open_map_filename = filedialog.askopenfilename(initialdir = self.preferences.GamePath, title = "Select file",filetypes = (("all files","*"),("all files with ext","*.*"),("jpeg files","*.jpg")))
		# Manage the user file selection
		if isinstance( open_map_filename, str ) and (open_map_filename != "") :
			# Note: when <type 'str'> # File selected, OK clicked
			if self.map_loaded == True:
				# If there is a map loaded, unload it before loading the new one
				self.UnloadMap()
			# Load the new map
			self.mapa_cargado = rceditor_maps.Map()
			logging.debug( "Cargando mapa " + open_map_filename )
			self.mapa_cargado.LoadFile( open_map_filename )
			self.loaded_map_filename = open_map_filename
			# aqui faltan muchas cosas mas ....
			logging.debug( "Representando mapa en editor... " )
			self.canvas_mapview.DrawAll( self.mapa_cargado )

			self.window_main_editor.title( "RoadCoin Level Editor - " + self.loaded_map_filename )
			self.map_loaded = True
			self.EnableMenuItems_MapLoaded()
		#elif isinstance( chosen_new_game_path, unicode ):
			# Note: when<type 'unicode'> # Nothing selected, Cancel clicked
		#elif isinstance( chosen_new_game_path, tuple ):
			# Note: when <type 'tuple'> # File selected, Cancel clicked
			# Note: when <type 'tuple'> # Multiple files selected, OK clicked


	def CloseMapButton(self):
		answer = tk.messagebox.askyesnocancel("Cerrar mapa", "¿Desea cerrar el mapa?")
		if (answer is not None) and (answer != False) :
			self.UnloadMap()


	def UnloadMap(self):
		del self.mapa_cargado
		logging.debug( "Mapa " + self.loaded_map_filename + " cerrado" )
		self.loaded_map_filename = None
		self.canvas_mapview.DisableViewer()
		self.window_main_editor.title( "RoadCoin Level Editor" )
		self.map_loaded = False
		self.DisableMenuItems_MapUnloaded()


	def ShowPreferencesWindowButton(self):
		logging.debug( "Abriendo ventana preferencias" )
		self.pref_window = rceditor_preferences.PreferencesWindow( master = self.window_main_editor,  preferences=self.preferences )


	def RedrawAllButton(self):
		self.canvas_mapview.DrawAll( self.mapa_cargado )


	def GoTo_Origin(self):
		self.canvas_mapview.GoTo_Origin()
		# self.canvas_mapview.zoomlevel = 1.0
		self.SetZoomLevel( 1.0 )
		self.canvas_mapview.DrawAll( self.mapa_cargado )


	def ChangeZoomLevel(self, zoom_increment ):
		if self.canvas_mapview.zoomlevel + zoom_increment > 0.01:
			self.canvas_mapview.zoomlevel += zoom_increment
			self.canvas_mapview.DrawAll( self.mapa_cargado )
			self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
			logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (incrementado)" )
		else:
			logging.debug("Ya estamos en el minimo zoom, no se cambia")


	def SetZoomLevel(self, zoomlevel):
		self.canvas_mapview.zoomlevel = zoomlevel
		self.canvas_mapview.DrawAll( self.mapa_cargado )
		self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
		logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (ajustado)" )



	def Update_Selected_Segment_Properties( self, segm_number ):
		# Write number and coords
		self.property_segm_number.set_value( segm_number )
		self.property_segm_start_x.set_value(  self.mapa_cargado.segment_dict.get(segm_number).start.x  ) 
		self.property_segm_start_y.set_value(  self.mapa_cargado.segment_dict.get(segm_number).start.y  )
		self.property_segm_end_x.set_value(  self.mapa_cargado.segment_dict.get(segm_number).end.x  ) 
		self.property_segm_end_y.set_value(  self.mapa_cargado.segment_dict.get(segm_number).end.y  ) 
		# Write segment type
		self.property_segm_type_variable.set( self.property_segm_type_choices[ self.mapa_cargado.segment_dict.get(segm_number).segm_type ] )
		# Write segment visibility
		if self.mapa_cargado.segment_dict.get(segm_number).invisible == True:
			self.property_segm_invis.select()
		else:
			self.property_segm_invis.deselect()

		
