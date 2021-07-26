# coding=UTF-8

import tkinter as tk
import logging
from enum import Enum
from PIL import ImageTk, Image		# Pillow
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from functools import partial
import sys
import math

#import rceditor_UI_operation
import rceditor_maps
import rceditor_mapview
import rceditor_preferences
import rceditor_custom_widgets
import rceditor_table_segm
import rceditor_table_bumper
import rceditor_table_raccz
import rceditor_help

import rceditor_lang


def do_nothing():
	x = 0

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


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
	Segment_SubMode.add		: "Submodo añadir segmento",
	Segment_SubMode.edit		: "Submodo editar segmento",
	# Segment_SubMode.delete		: "Submodo eliminar segmento"
}

class Segment_Add_Stages(Enum):
	St0_Choose_Start = 0		# Stage 0: Choose Starting Point
	St1_Choose_End = 1		# Stage 1: Choose Ending Point

class Bumper_SubMode(Enum):
	no_mode = 0
	add = 1
	edit = 2
	# delete = 3

bumper_submode_names = {
	Bumper_SubMode.no_mode		: "Ningun submodo seleccionado",
	Bumper_SubMode.add		: "Submodo añadir bumper",
	Bumper_SubMode.edit		: "Submodo editar bumper",
	# Bumper_SubMode.delete		: "Submodo eliminar bumper"
}

class Bumper_Add_Stages(Enum):
	St0_Choose_Center = 0		# Stage 0: Choose Center
	St1_Choose_Radius = 1		# Stage 1: Choose Radius

class RACCZ_SubMode(Enum):
	no_mode = 0
	add = 1
	edit = 2
	# delete = 3

raccz_submode_names = {
	RACCZ_SubMode.no_mode		: "Ningun submodo seleccionado",
	RACCZ_SubMode.add		: "Submodo añadir zona aceleracion circular",
	RACCZ_SubMode.edit		: "Submodo editar zona aceleracion circular",
	# RACCZ_SubMode.delete		: "Submodo eliminar zona aceleracion circular"
}

class RACCZ_Add_Stages(Enum):
	St0_Choose_Center = 0		# Stage 0: Choose Center
	St1_Choose_Radius = 1		# Stage 1: Choose Radius
	St2_Choose_Angle = 2		# Stage 2: Choose Angle
	

class General_SubMode(Enum):		# 13/2/2021
	no_mode = 0
	choose_coin_start_pos = 1
	choose_rotarion_center = 2

general_submode_names = {			# 13/2/2021
	General_SubMode.no_mode			: "Ningun submodo seleccionado",
	General_SubMode.choose_coin_start_pos	: "Submodo seleccionar posicion inicial moneda",
	General_SubMode.choose_rotarion_center	: "Submodo seleccionar centro giro mapa",
}

class RotBg_SubMode(Enum):		# 16/2/2021
	no_mode = 0
	choose_rotbg_center = 1

rotbg_submode_names = {			# 16/2/2021
	RotBg_SubMode.no_mode			: "Ningun submodo seleccionado",
	RotBg_SubMode.choose_rotbg_center	: "Submodo seleccionar posicion centro giro fondo giratorio",
}


##########################################################################

class RC_editor_GUI():

	current_mode = Mode.no_mode
	current_segment_submode = Segment_SubMode.no_mode
	current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start
	current_bumper_submode = Bumper_SubMode.no_mode
	current_bumper_add_stage = Bumper_Add_Stages.St0_Choose_Center
	current_raccz_submode = RACCZ_SubMode.no_mode
	current_raccz_add_stage = RACCZ_Add_Stages.St0_Choose_Center
	current_general_submode = General_SubMode.no_mode		# 14/2/2021
	current_rotbg_submode = RotBg_SubMode.no_mode			# 16/2/2021

	map_loaded = False
	loaded_map_filename = None
	segment_table = None
	bumper_table = None
	RACCZ_table = None
	temp_segment_data_to_create = rceditor_maps.Segment( start=rceditor_maps.Point(0,0), end=rceditor_maps.Point(0,0), segm_type=rceditor_maps.Segment_Type.wall, invisible=False )
	temp_pinball_bumper_data_to_create = rceditor_maps.Pinball_Bumper( center=rceditor_maps.Point(0,0), radius=0, exit_speed = 0 )
	temp_raccz_data_to_create = rceditor_maps.Round_Acceleration_Zone( center=rceditor_maps.Point(0,0), radius=0, angle=0, acceleration=0, invisible=False )
	snap_to_segm_point = False


	def __init__(self, debugmode=False ):
		logging.debug( "Cargando fichero de preferencias" )
		self.preferences = rceditor_preferences.Preferences()
		self.preferences.LoadPreferences()

		# Activate translations language (TODO 17/7/2021)
		_ = rceditor_lang.Initialize_Translations_Language(  self.preferences.Language  )

		logging.debug( "Inicializando ventana principal del editor" )
		self.window_main_editor = tk.Tk()
		self.window_main_editor.title( "RoadCoin Level Editor" )
		self.window_main_editor.minsize(600, 600)
		#self.window_main_editor.wm_iconbitmap('icon.ico')
		self.window_main_editor.protocol("WM_DELETE_WINDOW", self.window_close_button_handler)

		self.Load_UI_Icons()
		
		logging.debug( "Inicializando menu principal del editor" )
		self.menubar_mainmenu = tk.Menu( self.window_main_editor )
		self.filemenu = tk.Menu( self.menubar_mainmenu, tearoff=0)
		self.filemenu.add_command(label= _("Nuevo") , image = self.img_new_icon, compound = tk.LEFT, command = self.NewMapButton )
		self.filemenu.add_command(label= _("Abrir") , image = self.img_open_icon, compound = tk.LEFT, command = self.LoadMapButton )
		self.filemenu.add_command(label= _("Guardar") , image = self.img_save_icon, compound = tk.LEFT, command = self.SaveMapButton )			# 3/1/2021
		self.filemenu.add_command(label= _("Guardar como...") , image = self.img_save_icon, compound = tk.LEFT, command = self.SaveMapAsButton )	# 3/1/2021
		self.filemenu.add_command(label= _("Cerrar") , image = self.img_close_icon, compound = tk.LEFT, command=self.CloseMapButton )
		self.filemenu.add_separator()
		self.filemenu.add_command(label= _("Salir"), image = self.img_quit_icon, compound = tk.LEFT, command = self.window_main_editor.quit)
		self.menubar_mainmenu.add_cascade(label= _("Archivo") , menu = self.filemenu)
		self.editmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.editmenu.add_command(label= _("Deshacer") , command = do_nothing)
		self.editmenu.add_command(label= _("Rehacer") , command = do_nothing)
		self.editmenu.add_separator()
		self.editmenu.add_command(label= _("Preferencias...") , command = self.ShowPreferencesWindowButton )
		self.menubar_mainmenu.add_cascade(label= _("Editar") , menu=self.editmenu)
		self.viewmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.viewmenu.add_command(label= _("Redibujar todo") , image=self.img_reload_icon, compound = tk.LEFT, command = self.RedrawAllButton )
		self.viewmenu.add_separator()
		self.viewmenu.add_command(label= _("Volver a (0,0)") , image=self.img_origin_icon, compound = tk.LEFT, command = self.GoTo_Origin )
		self.menubar_mainmenu.add_cascade(label= _("Vista") , menu=self.viewmenu)
		self.helpmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
		self.helpmenu.add_command(label= "Help Index", command = do_nothing)
		self.helpmenu.add_command(label= _("About...") , command = self.AboutWindowButton)
		self.menubar_mainmenu.add_cascade(label= _("Ayuda") , menu=self.helpmenu)
		self.window_main_editor.config( menu = self.menubar_mainmenu )
		# Nota: añadir imagenes a los menus con image=self._img4, compound='left',...etc
		if debugmode==True:
			self.debugmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
			self.debugmenu.add_command(label= _("Verificar datos mapa") , command = self.Check_Map_Data)
			self.debugmenu.add_command(label= _("Reenumerar segmentos") , command = self.ReenumerateSegments)
			self.debugmenu.add_command(label= _("Actualizar propiedades") , command = self.Update_All_Properties)
			self.menubar_mainmenu.add_cascade(label="Debug", menu=self.debugmenu)		


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
		# self.canvas_mapview = tk.Canvas( master = self.frame_mapview )						# Without scrollbars
		self.canvas_mapview = rceditor_mapview.Canvas_WithScrollbars( master = self.frame_mapview, owner_object=self )	# With scrollbars
		self.canvas_mapview.pack(fill=tk.BOTH , expand=True )


		logging.debug( "Inicializando barra de estado" )
		#self.window_statusbar = StatusBar( self.window_main_editor )
		#self.window_statusbar.set("%s", "Holaaaaaaaa")
		#self.window_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
		self.window_statusbar = rceditor_custom_widgets.StatusBar_MultiFields( self.window_main_editor )
		self.window_statusbar.set_field_1("%s", _("Bienvenido al editor de niveles de Roadcoin") )
		self.window_statusbar.set_field_2("%s", _("CoordRaton") )	
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
		self.button_new_segm = tk.Button( master = self.frame_left_toolbar, text= _("Nuevo") , image=self.img_new_segm_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_SegmentSubMode, Segment_SubMode.add) )
		self.button_edit_segm = tk.Button( master = self.frame_left_toolbar, text= _("Editar") , image=self.img_edit_segm_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_SegmentSubMode, Segment_SubMode.edit ) )
		self.button_del_segm = tk.Button( master = self.frame_left_toolbar, text= _("Eliminar") , image=self.img_del_segm_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_Segment )
		self.button_table_segm = tk.Button( master = self.frame_left_toolbar, text= _("Tabla") , image=self.img_table_icon, compound=tk.LEFT, width=None, command = self.Toggle_Show_Hide_Segment_Table )
		self.button_snap_point_segm = tk.Button( master = self.frame_left_toolbar, text= _("Alinear") , image=self.img_snap_point_icon, compound=tk.LEFT, width=None, command = self.Toggle_SnapToPoint_Segm_Button )
		self.buttons_segm_list = [ self.button_new_segm, self.button_edit_segm, self.button_del_segm, self.button_table_segm, self.button_snap_point_segm ]
		# Bumpers mode buttons
		self.button_new_bumper = tk.Button( master = self.frame_left_toolbar, text= _("Nuevo") , image=self.img_new_bumper_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_BumperSubMode, Bumper_SubMode.add))
		self.button_edit_bumper = tk.Button( master = self.frame_left_toolbar, text= _("Editar") , image=self.img_edit_bumper_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_BumperSubMode, Bumper_SubMode.edit ) )
		self.button_del_bumper = tk.Button( master = self.frame_left_toolbar, text= _("Eliminar") , image=self.img_del_bumper_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_Bumper )
		self.button_table_bumper = tk.Button( master = self.frame_left_toolbar, text= _("Tabla") , image=self.img_table_icon, compound=tk.LEFT, width=None, command = self.Toggle_Show_Hide_Bumper_Table )
		self.buttons_bump_list = [ self.button_new_bumper, self.button_edit_bumper, self.button_del_bumper, self.button_table_bumper, self.button_snap_point_segm ]
		# RACCZ mode buttons
		self.button_new_raccz = tk.Button( master = self.frame_left_toolbar, text= _("Nuevo"), image=self.img_new_raccz_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_RACCZSubMode, RACCZ_SubMode.add))
		self.button_edit_raccz = tk.Button( master = self.frame_left_toolbar, text= _("Editar") , image=self.img_edit_raccz_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_RACCZSubMode, RACCZ_SubMode.edit ) )
		self.button_del_raccz = tk.Button( master = self.frame_left_toolbar, text= _("Eliminar") , image=self.img_del_raccz_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_RACCZ )
		self.button_table_raccz = tk.Button( master = self.frame_left_toolbar, text= _("Tabla") , image=self.img_table_icon, compound=tk.LEFT, width=None, command = self.Toggle_Show_Hide_RACCZ_Table )
		self.buttons_raccz_list = [ self.button_new_raccz, self.button_edit_raccz, self.button_del_raccz, self.button_table_raccz, self.button_snap_point_segm ]


		logging.debug( "Creando widgets del panel de propiedades para cada modo " )
		# Register validation methods
		General_RealNumber_Validation = self.window_main_editor.register(self.General_Property_RealNumber_Change_FocusOut_Validation_Callback)
		General_OPTIONAL_RealNumber_Validation =self.window_main_editor.register(self.General_Property_OPTIONAL_RealNumber_Change_FocusOut_Validation_Callback)
		General_String_Validation = self.window_main_editor.register(self.General_Property_String_Change_FocusOut_Validation_Callback)
		Image_String_Validation = self.window_main_editor.register(self.Image_Property_String_Change_FocusOut_Validation_Callback)
		RotBg_String_Validation = self.window_main_editor.register(self.RotBg_Property_String_Change_FocusOut_Validation_Callback)
		RotBg_RealNumber_Validation = self.window_main_editor.register(self.RotBg_Property_RealNumber_Change_FocusOut_Validation_Callback)
		RotBg_OPTIONAL_RealNumber_Validation = self.window_main_editor.register(self.RotBg_Property_OPTIONAL_RealNumber_Change_FocusOut_Validation_Callback)
		Segment_RealNumber_Validation = self.window_main_editor.register(self.Segment_Property_RealNumber_Change_FocusOut_Validation_Callback)
		Bumper_RealNumber_Validation = self.window_main_editor.register(self.Bumper_Property_RealNumber_Change_FocusOut_Validation_Callback)
		RACCZ_RealNumber_Validation = self.window_main_editor.register(self.RACCZ_Property_RealNumber_Change_FocusOut_Validation_Callback)
		# General mode properties widgets (21/1/2020)
		self.property_gen_map_name = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Nombre") , validatecommand=General_String_Validation )
		self.property_gen_description = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Descripcion") , validatecommand=General_String_Validation )
		self.property_gen_rot_type_label = tk.Label(master=self.frame_properties, text= _("Tipo rotacion mapa:") )
		self.property_gen_rot_type_variable = tk.StringVar()
		self.property_gen_rot_type_choices = [ rceditor_maps.Rotation_Type_Names.get(rceditor_maps.Rotation_Type.camera), \
							rceditor_maps.Rotation_Type_Names.get(rceditor_maps.Rotation_Type.fixed_point), \
							rceditor_maps.Rotation_Type_Names.get(rceditor_maps.Rotation_Type.coin), \
							rceditor_maps.Rotation_Type_Names.get(rceditor_maps.Rotation_Type.origin), \
							rceditor_maps.Rotation_Type_Names.get(rceditor_maps.Rotation_Type.no_rot)  ]
		self.property_gen_rot_type = tk.OptionMenu( self.frame_properties, self.property_gen_rot_type_variable, *self.property_gen_rot_type_choices, command=self.General_Property_OptionMenu_Click_Callback )
		self.property_gen_rot_center_label = tk.Label(master=self.frame_properties, text= _("Centro de giro mapa:") )
		self.property_gen_rot_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=General_OPTIONAL_RealNumber_Validation )
		self.property_gen_rot_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=General_OPTIONAL_RealNumber_Validation )
		self.property_gen_rot_center_select = tk.Button( master = self.frame_properties, text= _("Seleccionar centro giro") , command=self.Choose_Rotation_Center_Button_Callback )
		self.property_gen_max_angle = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Angulo maximo:") , validatecommand=General_RealNumber_Validation )
		self.property_gen_coin_start_pos_label = tk.Label(master=self.frame_properties,text="Posicion inicial moneda:")
		self.property_gen_coin_start_pos_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=General_RealNumber_Validation )
		self.property_gen_coin_start_pos_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=General_RealNumber_Validation )
		self.property_gen_coin_start_pos_select = tk.Button( master = self.frame_properties, text= _("Seleccionar pos incial") , command=self.Choose_Coin_Starting_Point_Button_Callback )
		self.property_gen_gravity = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Gravedad:") , validatecommand=General_RealNumber_Validation )
		self.property_gen_scale = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Escala:") , validatecommand=General_OPTIONAL_RealNumber_Validation )
		self.property_gen_music_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Musica") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_gen_timeout = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Tiempo cuenta atras:") , validatecommand=General_OPTIONAL_RealNumber_Validation )
		self.properties_gen_list = [ self.property_gen_map_name, self.property_gen_description, self.property_gen_rot_type_label, self.property_gen_rot_type, self.property_gen_rot_center_label, self.property_gen_rot_center_x, self.property_gen_rot_center_y, self.property_gen_rot_center_select, self.property_gen_max_angle, self.property_gen_coin_start_pos_label, self.property_gen_coin_start_pos_x, self.property_gen_coin_start_pos_y, self.property_gen_coin_start_pos_select, self.property_gen_gravity, self.property_gen_scale, self.property_gen_music_path, self.property_gen_timeout ]
		# Image mode properties widgets
		self.property_img_coin_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen moneda") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_img_background_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen fondo fijo") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_img_norot_coin_variable = tk.BooleanVar()
		self.property_img_norot_coin = tk.Checkbutton(master=self.frame_properties, text= _("Moneda no rota") , var=self.property_img_norot_coin_variable, command=self.Image_Property_Checkbox_Click_Callback )
		self.property_img_wall_segm_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen segmento pared") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_img_goal_segm_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen segmento meta") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_img_death_segm_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen segmento muerte") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.property_img_description_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen descripcion menu") , validatecommand=Image_String_Validation, initialdir=self.preferences.GamePath )
		self.properties_img_list = [ self.property_img_coin_path, self.property_img_background_path, self.property_img_norot_coin, self.property_img_wall_segm_path, self.property_img_goal_segm_path, self.property_img_death_segm_path, self.property_img_description_path ]
		# Rotating background mode properties widgets
		self.property_rotbg_exists_variable = tk.BooleanVar()
		self.property_rotbg_exists = tk.Checkbutton(master=self.frame_properties, text= _("Fondo giratorio") , var=self.property_rotbg_exists_variable, command=self.RotBg_Property_Checkbox_Click_Callback )
		self.property_rotbg_path = rceditor_custom_widgets.PathSelectionWithDescription( master=self.frame_properties, description= _("Imagen fondo giratorio"), validatecommand=RotBg_String_Validation, initialdir=self.preferences.GamePath )
		self.property_rotbg_pos_label = tk.Label(master=self.frame_properties,text= _("Posicion fondo giratorio:") )
		self.property_rotbg_left_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Izq X:") , validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_up_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Arriba Y:") , validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_right_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Der X:") , validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_down_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Abajo Y:") , validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_rot_center_pos_label = tk.Label(master=self.frame_properties,text= _("Centro giro fondo giratorio:") )
		self.property_rotbg_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=RotBg_OPTIONAL_RealNumber_Validation )
		self.property_rotbg_center_select = tk.Button( master = self.frame_properties, text= _("Seleccionar centro giro") , command=self.Choose_Rotating_Background_Rotation_Center_Button_Callback )
		self.properties_rotbg_list = [ self.property_rotbg_exists, self.property_rotbg_path, self.property_rotbg_pos_label, self.property_rotbg_left_x, self.property_rotbg_up_y, self.property_rotbg_right_x, self.property_rotbg_down_y, self.property_rotbg_rot_center_pos_label, self.property_rotbg_center_x, self.property_rotbg_center_y, self.property_rotbg_center_select ]
		# Segment mode properties widgets
		self.property_segm_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Numero segmento:") , validatecommand=do_nothing, state='readonly' )
		self.property_segm_start_label = tk.Label(master=self.frame_properties,text="Start:")
		self.property_segm_start_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_start_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_end_label = tk.Label(master=self.frame_properties,text="End:")
		self.property_segm_end_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_end_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_type_label = tk.Label(master=self.frame_properties, text= _("Tipo segmento:") )
		self.property_segm_type_variable = tk.StringVar()
		self.property_segm_type_choices = [ rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.wall), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.goal), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.death), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_L), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_R)  ]
		self.property_segm_type = tk.OptionMenu( self.frame_properties, self.property_segm_type_variable, *self.property_segm_type_choices, command=self.Segment_Property_OptionMenu_Click_Callback )
		self.property_segm_invis_variable = tk.BooleanVar()
		self.property_segm_invis = tk.Checkbutton(master=self.frame_properties, text= _("Invisible") , var=self.property_segm_invis_variable, command=self.Segment_Property_Checkbox_Click_Callback )
		self.property_segm_apply = tk.Button( master = self.frame_properties, text= _("Forzar aplicar cambios") , command = self.Apply_Selected_Segment_Changes)
		self.properties_segm_list = [ self.property_segm_number, self.property_segm_start_label, self.property_segm_start_x, self.property_segm_start_y, self.property_segm_end_label, self.property_segm_end_x, self.property_segm_end_y, self.property_segm_type_label, self.property_segm_type, self.property_segm_type, self.property_segm_invis, self.property_segm_apply ]
		# Bumpers mode properties widgets
		self.property_bumper_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Numero bumper:") , validatecommand=do_nothing, state='readonly' )
		self.property_bumper_center_label = tk.Label(master=self.frame_properties,text= _("Centro:") )
		self.property_bumper_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_radius_label = tk.Label(master=self.frame_properties,text= _("Radio:") )
		self.property_bumper_radius = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Radio:") , validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_speed_label = tk.Label(master=self.frame_properties, text= _("Velocidad de salida:") )
		self.property_bumper_speed = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("V salida:") , validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_apply = tk.Button( master = self.frame_properties, text= _("Forzar aplicar cambios") , command = self.Apply_Selected_Bumper_Changes)
		self.properties_bump_list = [ self.property_bumper_number, self.property_bumper_center_label, self.property_bumper_center_x, self.property_bumper_center_y, self.property_bumper_radius_label, self.property_bumper_radius, self.property_bumper_speed_label, self.property_bumper_speed, self.property_bumper_apply ]
		# RACCZ mode properties widgets
		self.property_raccz_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Numero bumper:") , validatecommand=do_nothing, state='readonly' )
		self.property_raccz_center_label = tk.Label(master=self.frame_properties,text= _("Centro:") )
		self.property_raccz_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_radius_label = tk.Label(master=self.frame_properties,text= _("Radio:") )
		self.property_raccz_radius = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Radio:") , validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_angle_label = tk.Label(master=self.frame_properties,text= _("Angulo:") )
		self.property_raccz_angle = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Angulo:") , validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_accel_label = tk.Label(master=self.frame_properties, text= _("Aceleracion:") )
		self.property_raccz_accel = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description= _("Aceleracion:") , validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_invis_variable = tk.BooleanVar()
		self.property_raccz_invis = tk.Checkbutton(master=self.frame_properties, text= _("Invisible") , var=self.property_raccz_invis_variable, command=self.RACCZ_Property_Checkbox_Click_Callback )
		self.property_raccz_apply = tk.Button( master = self.frame_properties, text= _("Forzar aplicar cambios") , command = self.Apply_Selected_RACCZ_Changes)
		self.properties_raccz_list = [ self.property_raccz_number, self.property_raccz_center_label, self.property_raccz_center_x, self.property_raccz_center_y, self.property_raccz_radius_label, self.property_raccz_radius, self.property_raccz_angle_label, self.property_raccz_angle, self.property_raccz_accel_label, self.property_raccz_accel, self.property_raccz_invis, self.property_raccz_apply ]


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
		# Unselect everything (segments, bumpers, raccz, etc) when mode changes
		self.Unselect_All()


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
		#elif self.current_segment_submode == Segment_SubMode.delete:
		#	self.button_del_segm.configure( bg = self.orig_button_bg_color )

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
				current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start
				self.window_statusbar.set_field_1("%s", _("Nuevo segmento: seleccione punto inicial") )
				self.canvas_mapview.Set_Cursor_Cross()
			elif new_segment_submode == Segment_SubMode.edit:
				self.button_edit_segm.configure( bg = "green" )
				self.window_statusbar.set_field_1("%s", _("Seleccione un segmento") )
				self.canvas_mapview.Set_Cursor_Arrow()
			#elif new_segment_submode == Segment_SubMode.delete:
			#	self.button_del_segm.configure( bg = "green" )
			# Actions to do regardless of the new mode
			self.button_del_segm.config(state="disabled")		# Disable erase button (15/11/2020)
			self.current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start	# Restart "add new segment" sequence
			self.canvas_mapview.Hide_SegmentBeingCreated( )		# Delete previews of items in process of creation (if any)
			self.canvas_mapview.Hide_PinballBumperBeingCreated( )
			self.canvas_mapview.Hide_RACCZ_BeingCreated( )


	def Reconf_UI_To_BumperSubMode(self, new_bumper_submode):
		# Restore colors of old mode button
		if self.current_bumper_submode == Bumper_SubMode.add:
			self.button_new_bumper.configure( bg = self.orig_button_bg_color )
		elif self.current_bumper_submode == Bumper_SubMode.edit:
			self.button_edit_bumper.configure( bg = self.orig_button_bg_color )
		#elif self.current_bumper_submode == Bumper_SubMode.delete:
		#	self.button_del_bumper.configure( bg = self.orig_button_bg_color )

		if new_bumper_submode == self.current_bumper_submode:
			logging.debug( "Ningun submodo bumper seleccionado")
			
			self.current_bumper_submode = Bumper_SubMode.no_mode
			return
		else:
			logging.debug( "Activando submodo bumper " + bumper_submode_names.get(new_bumper_submode) )
			self.current_bumper_submode = new_bumper_submode
			# Draw color of new mode button
			if new_bumper_submode == Bumper_SubMode.add:
				self.button_new_bumper.configure( bg = "green" )
				current_bumper_add_stage = Bumper_Add_Stages.St0_Choose_Center
				self.window_statusbar.set_field_1("%s", _("Nuevo bumper: seleccione punto central") )
				self.canvas_mapview.Set_Cursor_Cross()
			elif new_bumper_submode == Bumper_SubMode.edit:
				self.button_edit_bumper.configure( bg = "green" )
				self.window_statusbar.set_field_1("%s", _("Seleccione un bumper") )
				self.canvas_mapview.Set_Cursor_Arrow()
			#elif new_bumper_submode == Bumper_SubMode.delete:
			#	self.button_del_bumper.configure( bg = "green" )
			self.button_del_bumper.config(state="disabled")	# Disable erase button (7/12/2020)
			self.current_bumper_add_stage = Bumper_Add_Stages.St0_Choose_Center	# Restart "add new bumper" sequence
			self.canvas_mapview.Hide_SegmentBeingCreated( )		# Delete previews of items in process of creation (if any)
			self.canvas_mapview.Hide_PinballBumperBeingCreated( )
			self.canvas_mapview.Hide_RACCZ_BeingCreated( )
 

	def Reconf_UI_To_RACCZSubMode(self, new_raccz_submode):
		# Restore colors of old mode button
		if self.current_raccz_submode == RACCZ_SubMode.add:
			self.button_new_raccz.configure( bg = self.orig_button_bg_color )
		elif self.current_raccz_submode == RACCZ_SubMode.edit:
			self.button_edit_raccz.configure( bg = self.orig_button_bg_color )
		#elif self.current_raccz_submode == RACCZ_SubMode.delete:
		#	self.button_del_raccz.configure( bg = self.orig_button_bg_color )

		if new_raccz_submode == self.current_raccz_submode:
			logging.debug( "Ningun submodo de zona de aceleracion circular seleccionado")
			
			self.current_raccz_submode = RACCZ_SubMode.no_mode
			return
		else:
			logging.debug( "Activando submodo RACCZ " + raccz_submode_names.get(new_raccz_submode) )
			self.current_raccz_submode = new_raccz_submode
			# Draw color of new mode button
			if new_raccz_submode == RACCZ_SubMode.add:
				self.button_new_raccz.configure( bg = "green" )
				current_raccz_add_stage = RACCZ_Add_Stages.St0_Choose_Center
				self.window_statusbar.set_field_1("%s", _("Nueva zona acel circular: seleccione punto central") )
				self.canvas_mapview.Set_Cursor_Cross()
			elif new_raccz_submode == RACCZ_SubMode.edit:
				self.button_edit_raccz.configure( bg = "green" )
				self.window_statusbar.set_field_1("%s", _("Seleccione una zona de aceleracion circular") )
				self.canvas_mapview.Set_Cursor_Arrow()
			#elif new_raccz_submode == RACCZ_SubMode.delete:
			#	self.button_del_raccz.configure( bg = "green" )
			self.button_del_raccz.config(state="disabled")	# Disable erase button (7/12/2020)
			self.current_raccz_add_stage = RACCZ_Add_Stages.St0_Choose_Center		# Restart "add new raccz" sequence
			self.canvas_mapview.Hide_SegmentBeingCreated( )		# Delete previews of items in process of creation (if any)
			self.canvas_mapview.Hide_PinballBumperBeingCreated( )
			self.canvas_mapview.Hide_RACCZ_BeingCreated( )


	def EnableMenuItems_MapLoaded( self ):
		self.filemenu.entryconfig( _("Cerrar") , state="normal")
		self.editmenu.entryconfig( _("Deshacer") , state="normal")
		self.editmenu.entryconfig( _("Rehacer") , state="normal")
		self.viewmenu.entryconfig( _("Redibujar todo") , state="normal")
		self.viewmenu.entryconfig( _("Volver a (0,0)") , state="normal")

	def DisableMenuItems_MapUnloaded( self ):
		self.filemenu.entryconfig( _("Cerrar") , state="disabled")
		self.editmenu.entryconfig( _("Deshacer") , state="disabled")
		self.editmenu.entryconfig( _("Rehacer") , state="disabled")
		self.viewmenu.entryconfig( _("Redibujar todo") , state="disabled")
		self.viewmenu.entryconfig( _("Volver a (0,0)") , state="disabled")

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

		self.img_new_raccz_icon = ImageTk.PhotoImage(Image.open("icons/new_raccz-16.png"))
		self.img_edit_raccz_icon = ImageTk.PhotoImage(Image.open("icons/edit_raccz-16.png"))
		self.img_del_raccz_icon = ImageTk.PhotoImage(Image.open("icons/del_raccz-16.png"))

		self.img_new_bumper_icon = ImageTk.PhotoImage(Image.open("icons/new_bumper-16.png"))
		self.img_edit_bumper_icon = ImageTk.PhotoImage(Image.open("icons/edit_bumper-16.png"))
		self.img_del_bumper_icon = ImageTk.PhotoImage(Image.open("icons/del_bumper-16.png"))

		self.img_table_icon = ImageTk.PhotoImage(Image.open("icons/table-16.png"))

		self.img_snap_point_icon = ImageTk.PhotoImage(Image.open("icons/snap_to_point-16.png"))



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
			
			if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.add:
				if ( self.snap_to_segm_point == True ):
					# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
					map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
					if snap == True:
						self.canvas_mapview.Show_TargetBox( map_x, map_y )
					else:
						self.canvas_mapview.Hide_TargetBox( )

				if ( self.current_segment_add_stage == Segment_Add_Stages.St1_Choose_End ):
					# We are adding a new line segment. Draw line as preview.
					self.canvas_mapview.Show_SegmentBeingCreated( self.temp_segment_data_to_create.start.x, self.temp_segment_data_to_create.start.y, map_x, map_y )

			if self.current_mode == Mode.bumper and self.current_bumper_submode == Bumper_SubMode.add:
				if ( self.snap_to_segm_point == True ):
					# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
					map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
					if snap == True:
						self.canvas_mapview.Show_TargetBox( map_x, map_y )
					else:
						self.canvas_mapview.Hide_TargetBox( )

				if ( self.current_bumper_add_stage == Bumper_Add_Stages.St1_Choose_Radius ):
					# We are adding a new pinball bumper. Draw circle as preview.
					# Calculate the radius
					preview_radius = math.sqrt( ( map_x - self.temp_pinball_bumper_data_to_create.center.x )**2 + ( map_y - self.temp_pinball_bumper_data_to_create.center.y )**2 )
					self.canvas_mapview.Show_PinballBumperBeingCreated( self.temp_pinball_bumper_data_to_create.center.x, self.temp_pinball_bumper_data_to_create.center.y, preview_radius )
			if self.current_mode == Mode.round_accel_zone and self.current_raccz_submode == RACCZ_SubMode.add:
				if ( self.snap_to_segm_point == True ):
					# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
					map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
					if snap == True:
						self.canvas_mapview.Show_TargetBox( map_x, map_y )
					else:
						self.canvas_mapview.Hide_TargetBox( )

				if ( self.current_raccz_add_stage == RACCZ_Add_Stages.St1_Choose_Radius ):
					# We are adding a new round acceleration zone. Draw circle as preview.
					# Calculate the radius
					preview_radius = math.sqrt( ( map_x - self.temp_raccz_data_to_create.center.x )**2 + ( map_y - self.temp_raccz_data_to_create.center.y )**2 )
					self.canvas_mapview.Show_RACCZ_BeingCreated( self.temp_raccz_data_to_create.center.x, self.temp_raccz_data_to_create.center.y, preview_radius, angle=None )
				if ( self.current_raccz_add_stage == RACCZ_Add_Stages.St2_Choose_Angle ):
					# We are adding a new round acceleration zone. Draw circle and an arrow as preview.
					# # Calculate the radius
					# preview_radius = math.sqrt( ( map_x - self.temp_raccz_data_to_create.center.x )**2 + ( map_y - self.temp_raccz_data_to_create.center.y )**2 )
					# Calculate the angle
					preview_angle = math.degrees( math.atan2( map_y - self.temp_raccz_data_to_create.center.y  ,  map_x - self.temp_raccz_data_to_create.center.x  )  ) +90
					self.canvas_mapview.Show_RACCZ_BeingCreated( self.temp_raccz_data_to_create.center.x, self.temp_raccz_data_to_create.center.y, radius = self.temp_raccz_data_to_create.radius, angle=preview_angle )



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
			canvas_x = self.canvas_mapview.viewer.canvasx(event.x)	# Canvas coordinates
			canvas_y = self.canvas_mapview.viewer.canvasy(event.y)
			map_x = int(canvas_x / self.canvas_mapview.zoomlevel)	# Map coordinates
			map_y = int(canvas_y / self.canvas_mapview.zoomlevel)
			logging.debug("Pulsado boton " + str( event.num ) + " en x=" + str(map_x) + ", y=" + str(map_y) +", modo = " + mode_names.get( self.current_mode ) )
			if event.num == 1:	# Left mouse button clicked
				if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.edit:
					# logging.debug("Los objetos proximos son " + str( self.canvas_mapview.viewer.find_closest(canvas_x, canvas_y) ) )
					logging.debug("Los objetos encima son " + str( self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10) ) )
					# canvas_object_found = self.canvas_mapview.viewer.find_closest(canvas_x, canvas_y)[0]
					canvas_object_found_list = self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10)
					# logging.debug("Encontrado objeto con identificador " + str( canvas_object_found ) + " en el lienzo" )
					segment_found = None
					for canvas_object_found in canvas_object_found_list:
						if canvas_object_found in self.canvas_mapview.segment_lines_dict:
							segment_found = self.canvas_mapview.segment_lines_dict.get(canvas_object_found)
							logging.debug("Encontrado segmento " + str( segment_found ) )
							break
						elif canvas_object_found in self.canvas_mapview.segment_num_texts_dict:
							segment_found = self.canvas_mapview.segment_num_texts_dict.get(canvas_object_found)
							logging.debug("Encontrado texto numero segmento " + str( segment_found ) )
							break
						else:
							# We found something that was not a line segment
							continue 
					
					if segment_found is not None:
						self.canvas_mapview.UnHighlight_Segments()
						self.canvas_mapview.Highlight_Segments( [ segment_found ] )		# Type cast into list
						self.Update_Selected_Segment_Properties( segment_found )
						self.window_statusbar.set_field_1("%s %d %s", _("Segmento ") , segment_found ,  _(" seleccionado") )
					else:
						logging.debug("No se ha encontrado ningun segmento.")
						self.UnSelect_Segment()
						self.canvas_mapview.UnHighlight_Segments()
						self.window_statusbar.set_field_1("%s", _("Segmentos deseleccionados") )

				if self.current_mode == Mode.bumper and self.current_bumper_submode == Bumper_SubMode.edit:
					logging.debug("Los objetos encima son " + str( self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10) ) )
					canvas_object_found_list = self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10)
					bumper_found = None
					for canvas_object_found in canvas_object_found_list:
						if canvas_object_found in self.canvas_mapview.bumpers_dict:
							bumper_found = self.canvas_mapview.bumpers_dict.get(canvas_object_found)
							logging.debug("Encontrado bumper " + str( bumper_found ) )
							break
						elif canvas_object_found in self.canvas_mapview.bumpers_num_texts_dict:
							bumper_found = self.canvas_mapview.bumpers_num_texts_dict.get(canvas_object_found)
							logging.debug("Encontrado texto numero bumper " + str( bumper_found ) )
							break
						else:
							# We found something that was not a bumper
							continue 
					
					if bumper_found is not None:
						self.canvas_mapview.UnHighlight_Bumpers()
						self.canvas_mapview.Highlight_Bumpers( [ bumper_found ] )		# Type cast into list
						self.Update_Selected_Bumper_Properties( bumper_found )
						self.window_statusbar.set_field_1("%s %d %s", "Bumper ", bumper_found ," seleccionado" )
					else:
						logging.debug("No se ha encontrado ningun bumper.")
						self.UnSelect_Bumper()
						self.canvas_mapview.UnHighlight_Bumpers()
						self.window_statusbar.set_field_1("%s", _("Bumpers deseleccionados") )

				if self.current_mode == Mode.round_accel_zone and self.current_raccz_submode == RACCZ_SubMode.edit:
					logging.debug("Los objetos encima son " + str( self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10) ) )
					canvas_object_found_list = self.canvas_mapview.viewer.find_overlapping(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10)
					raccz_found = None
					for canvas_object_found in canvas_object_found_list:
						if canvas_object_found in self.canvas_mapview.raccz_dict:
							raccz_found = self.canvas_mapview.raccz_dict.get(canvas_object_found)
							logging.debug("Encontrado poligono de zona de aceleracion circular " + str( raccz_found ) )
							break
						if canvas_object_found in self.canvas_mapview.raccz_circles_dict:
							raccz_found = self.canvas_mapview.raccz_circles_dict.get(canvas_object_found)
							logging.debug("Encontrado circulo de zona de aceleracion circular " + str( raccz_found ) )
							break
						elif canvas_object_found in self.canvas_mapview.raccz_num_texts_dict:
							raccz_found = self.canvas_mapview.raccz_num_texts_dict.get(canvas_object_found)
							logging.debug("Encontrado texto numero zona de aceleracion circular " + str( raccz_found ) )
							break
						else:
							# We found something that was not a round acceleration zone
							continue 
					
					if raccz_found is not None:
						self.canvas_mapview.UnHighlight_RACCZ()
						self.canvas_mapview.Highlight_RACCZ( [ raccz_found ] )		# Type cast into list
						self.Update_Selected_RACCZ_Properties( raccz_found )
						self.window_statusbar.set_field_1("%s %d %s", _("Zona acel circ ") , raccz_found , _(" seleccionada") )
					else:
						logging.debug("No se ha encontrado ninguna zona de aceleracion circular.")
						self.UnSelect_RACCZ()
						self.canvas_mapview.UnHighlight_RACCZ()
						self.window_statusbar.set_field_1("%s", _("Zonas acel circ deseleccionadas") )

				if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.add:
					if ( self.current_segment_add_stage == Segment_Add_Stages.St0_Choose_Start):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
						logging.debug( "Seleccionado como punto inicial: x = " + str(map_x) + ", y = " + str(map_y) )
						self.temp_segment_data_to_create.start.x = map_x
						self.temp_segment_data_to_create.start.y = map_y
						self.window_statusbar.set_field_1("%s",  _("Nuevo segmento: seleccione punto final") )
						self.current_segment_add_stage = Segment_Add_Stages.St1_Choose_End
					elif ( self.current_segment_add_stage == Segment_Add_Stages.St1_Choose_End):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
						logging.debug( "Seleccionado como punto final: x = " + str(map_x) + ", y = " + str(map_y) )
						self.temp_segment_data_to_create.end.x = map_x
						self.temp_segment_data_to_create.end.y = map_y
						# We set the "segment type" property that is currently displayed in the properties frame
						read_segm_type = self.property_segm_type_variable.get()
						if ( read_segm_type != "" ) and ( read_segm_type is not None ):
							for type_num, segm_type_to_compare in enumerate(self.property_segm_type_choices, start=0) :
								if read_segm_type == segm_type_to_compare:
									self.temp_segment_data_to_create.segm_type = type_num
									break	# Exit for
						else:
							self.temp_segment_data_to_create.segm_type = rceditor_maps.Segment_Type.wall.value	# In case nothing is selected, set a default type
						logging.debug( "Nuevo segmento: tipo de segmento " + rceditor_maps.Segment_Type_Names.get( rceditor_maps.Segment_Type(self.temp_segment_data_to_create.segm_type) )  )
						# We set the "visibility" property that is currently displayed in the properties frame
						self.temp_segment_data_to_create.invisible = self.property_segm_invis_variable.get() 
						# Create segment
						self.mapa_cargado.AddSegment( self.temp_segment_data_to_create )
						# Draw it
						self.canvas_mapview.DrawSingleSegment( Map=self.mapa_cargado, num_segm=self.mapa_cargado.segment_number-1 )
						self.canvas_mapview.DrawSingleSegmentNumber( Map=self.mapa_cargado, num_segm=self.mapa_cargado.segment_number-1 )
						# Clear all data in temporal segment data
						self.temp_segment_data_to_create.start.x = None
						self.temp_segment_data_to_create.start.y = None
						self.temp_segment_data_to_create.end.x = None
						self.temp_segment_data_to_create.end.y = None
						self.temp_segment_data_to_create.segm_type = None
						self.temp_segment_data_to_create.invisible = None
						# Change stage
						self.window_statusbar.set_field_1("%s", _("Nuevo segmento: seleccione punto inicial") )
						self.current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start
						# We delete the segment preview (26/11/2020)
						self.canvas_mapview.Hide_SegmentBeingCreated( )

						### Redraw segment table (if the table is displayed)  # 16/3/2021
						if self.segment_table is not None:
							logging.debug( "La interfaz principal indica a la tabla de segmentos que debe actualizarse." )
							self.segment_table.update_table_from_map_editor()

					else:
						logging.error( _("Error de programacion: etapa actual de añadir segmento tiene un valor no valido ") + str(self.current_segment_add_stage) )

				if self.current_mode == Mode.bumper and self.current_bumper_submode == Bumper_SubMode.add:
					if ( self.current_bumper_add_stage == Bumper_Add_Stages.St0_Choose_Center ):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
						logging.debug( "Seleccionado como punto central: x = " + str(map_x) + ", y = " + str(map_y) )
						self.temp_pinball_bumper_data_to_create.center.x = map_x
						self.temp_pinball_bumper_data_to_create.center.y = map_y
						self.window_statusbar.set_field_1("%s", _("Nuevo bumper: seleccione radio (clic en un punto de la circunferencia)") )
						self.current_bumper_add_stage = Bumper_Add_Stages.St1_Choose_Radius
					elif ( self.current_bumper_add_stage == Bumper_Add_Stages.St1_Choose_Radius ):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )							
						logging.debug( "Seleccionado como punto de la circunferencia: x = " + str(map_x) + ", y = " + str(map_y) )
						# Calculate the radius
						self.temp_pinball_bumper_data_to_create.radius = math.sqrt( ( map_x - self.temp_pinball_bumper_data_to_create.center.x )**2 + ( map_y - self.temp_pinball_bumper_data_to_create.center.y )**2 )
						# Ask for the exit speed
						exit_speed_answer = simpledialog.askfloat( _("Velocidad de salida"), _("Velocidad de salida:"), parent=self.window_main_editor, initialvalue=50, minvalue=0.0, maxvalue=100000.0) 
						if (exit_speed_answer is not None ):
							self.temp_pinball_bumper_data_to_create.exit_speed = float(exit_speed_answer)
							# Create bumper
							self.mapa_cargado.AddPinballBumper( self.temp_pinball_bumper_data_to_create )
							# Draw it
							self.canvas_mapview.DrawSingleBumper( Map=self.mapa_cargado, num_bumper=self.mapa_cargado.pinball_bumpers_number-1 )
							self.canvas_mapview.DrawSingleBumperNumber( Map=self.mapa_cargado, num_bumper=self.mapa_cargado.pinball_bumpers_number-1 )
						else:
							tk.messagebox.showwarning(title= _("Aviso") , message= _("No se ha creado el bumper.") )
						# Clear all data in temporal bumper data
						self.temp_pinball_bumper_data_to_create.center.x = None
						self.temp_pinball_bumper_data_to_create.center.y = None
						self.temp_pinball_bumper_data_to_create.radius = None
						self.temp_pinball_bumper_data_to_create.exit_speed = None
						# Change stage
						self.window_statusbar.set_field_1("%s", _("Nuevo bumper: seleccione punto central") )
						self.current_bumper_add_stage = Bumper_Add_Stages.St0_Choose_Center
						# We delete the bumper preview
						self.canvas_mapview.Hide_PinballBumperBeingCreated( )

						### Redraw bumper table (if the table is displayed)  # 18/3/2021
						if self.bumper_table is not None:
							logging.debug( "La interfaz principal indica a la tabla de bumpers que debe actualizarse." )
							self.bumper_table.update_table_from_map_editor()

					else:
						logging.error( _("Error de programacion: etapa actual de añadir bumper tiene un valor no valido ") + str(self.current_bumper_add_stage) )



				if self.current_mode == Mode.round_accel_zone and self.current_raccz_submode == RACCZ_SubMode.add:
					if ( self.current_raccz_add_stage == RACCZ_Add_Stages.St0_Choose_Center ):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
							logging.debug( "Seleccionado como punto inicial: x = " + str(map_x) + ", y = " + str(map_y) )
						logging.debug( "Seleccionado como punto central: x = " + str(map_x) + ", y = " + str(map_y) )
						self.temp_raccz_data_to_create.center.x = map_x
						self.temp_raccz_data_to_create.center.y = map_y
						self.window_statusbar.set_field_1("%s", _("Nueva zona acel circular: seleccione radio (clic en un punto de la circunferencia)") )
						self.current_raccz_add_stage = RACCZ_Add_Stages.St1_Choose_Radius

					elif ( self.current_raccz_add_stage == RACCZ_Add_Stages.St1_Choose_Radius ):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
							logging.debug( "Seleccionado como punto inicial: x = " + str(map_x) + ", y = " + str(map_y) )
						logging.debug( "Seleccionado como punto de la circunferencia: x = " + str(map_x) + ", y = " + str(map_y) )
						# Calculate the radius
						self.temp_raccz_data_to_create.radius = math.sqrt( ( map_x - self.temp_raccz_data_to_create.center.x )**2 + ( map_y - self.temp_raccz_data_to_create.center.y )**2 )
						self.window_statusbar.set_field_1("%s", _("Nueva zona acel circular: seleccione direccion (clic en un punto que defina el angulo)") )
						self.current_raccz_add_stage = RACCZ_Add_Stages.St2_Choose_Angle

					elif ( self.current_raccz_add_stage == RACCZ_Add_Stages.St2_Choose_Angle ):
						if ( self.snap_to_segm_point == True ):
							# Snap to point is selected. We search for a point (segm start or end) near to current mouse position. If found, we use this point coordinates
							map_x, map_y, snap = self.mapa_cargado.FindNearestSegmentPoint( point=rceditor_maps.Point( x=map_x, y=map_y) , threshold= self.preferences.SnapTo_Threshold )
							logging.debug( "Seleccionado como punto inicial: x = " + str(map_x) + ", y = " + str(map_y) )
						logging.debug( "Seleccionado como punto de la dirección: x = " + str(map_x) + ", y = " + str(map_y) )
						# Calculate the direction
						self.temp_raccz_data_to_create.angle = math.degrees(  math.atan2( map_y - self.temp_raccz_data_to_create.center.y ,  map_x - self.temp_raccz_data_to_create.center.x ) ) +90
						# We set the "visibility" property that is currently displayed in the properties frame
						self.temp_raccz_data_to_create.invisible = self.property_raccz_invis_variable.get() 
						# Ask for acceleration
						acceleration_answer = simpledialog.askfloat( _("Aceleracion") , _("Aceleracion:") , parent=self.window_main_editor, initialvalue=50, minvalue=0.0, maxvalue=100000.0)
						# self.temp_raccz_data_to_create.acceleration = float( simpledialog.askfloat("Aceleracion", "Aceleracion:", parent=self.window_main_editor, initialvalue=50, minvalue=0.0, maxvalue=100000.0) )
						# if (self.temp_raccz_data_to_create.acceleration is not None ):
						if ( acceleration_answer is not None ):
							self.temp_raccz_data_to_create.acceleration = float( acceleration_answer )
							# Create round acceleration zone
							self.mapa_cargado.AddRACCZ( self.temp_raccz_data_to_create )
							# Draw it
							self.canvas_mapview.DrawSingleRACCZ( Map=self.mapa_cargado, num_raccz=self.mapa_cargado.round_accel_zones_number-1 )
							self.canvas_mapview.DrawSingleRACCZNumber( Map=self.mapa_cargado, num_raccz=self.mapa_cargado.round_accel_zones_number-1 )
						else:
							tk.messagebox.showwarning(title= _("Aviso") , message= _("No se ha creado la zona circular de aceleracion.") )
						# Clear all data in temporal raccz data
						self.temp_raccz_data_to_create.center.x = None
						self.temp_raccz_data_to_create.center.y = None
						self.temp_raccz_data_to_create.radius = None
						self.temp_raccz_data_to_create.acceleration = None
						self.temp_raccz_data_to_create.invisible = None
						# Change stage
						self.window_statusbar.set_field_1("%s", _("Nueva zona acel circular: seleccione punto central") )
						self.current_raccz_add_stage = RACCZ_Add_Stages.St0_Choose_Center
						# We delete the raccz preview
						self.canvas_mapview.Hide_RACCZ_BeingCreated(  )

						### Redraw raccz table (if the table is displayed)  # 21/3/2021
						if self.RACCZ_table is not None:
							logging.debug( "La interfaz principal indica a la tabla de zonas de aceleracion circular que debe actualizarse." )
							self.RACCZ_table.update_table_from_map_editor()

					else:
						logging.error( _("Error de programacion: etapa actual de añadir raccz tiene un valor no valido ")  + str(self.current_raccz_add_stage) )	

				if self.current_mode == Mode.general and self.current_general_submode == General_SubMode.choose_coin_start_pos:	# 14/2/2021
					logging.debug( "Seleccionado como punto inicio moneda: x = " + str(map_x) + ", y = " + str(map_y) )
					# Save new position on map data
					self.mapa_cargado.coin_starting_point.x = map_x
					self.mapa_cargado.coin_starting_point.y = map_y
					# Update general properties on the frame properties
					self.Update_General_Properties()
					# Redraw new coin position
					self.canvas_mapview.Show_Coin_Start_Position( self.mapa_cargado )
					# Change submode to no mode
					self.current_general_submode = General_SubMode.no_mode
					self.window_statusbar.set_field_1("%s", _("Posicion inicial de la moneda actualizada") )
					self.canvas_mapview.Set_Cursor_Arrow()
				if self.current_mode == Mode.general and self.current_general_submode == General_SubMode.choose_rotarion_center:	# 15/2/2021
					logging.debug( "Seleccionado como punto giro mapa: x = " + str(map_x) + ", y = " + str(map_y) )
					# Save new position on map data
					self.mapa_cargado.rotation_center.x = map_x
					self.mapa_cargado.rotation_center.y = map_y
					# Update general properties on the frame properties
					self.Update_General_Properties()
					# Redraw new rotation center
					self.canvas_mapview.Show_Rotation_Center( self.mapa_cargado )
					# Change submode to no mode
					self.current_general_submode = General_SubMode.no_mode
					self.window_statusbar.set_field_1("%s", _("Centro de giro actualizado") )
					self.canvas_mapview.Set_Cursor_Arrow()

				if self.current_mode == Mode.rot_bg and self.current_rotbg_submode == RotBg_SubMode.choose_rotbg_center:	# 16/2/2021
					logging.debug( "Seleccionado como punto centro giro fondo giratorio: x = " + str(map_x) + ", y = " + str(map_y) )
					# Calculate rotating background rotation center and save new position on map data
					# NOTE: These are not absolute coordinates, they are coordinates relative to the texture left corner
					# Note: This is how roadcoin is currently programmed
					self.mapa_cargado.rotating_background_center.x = map_x - self.mapa_cargado.rotating_background_left_x_pos
					self.mapa_cargado.rotating_background_center.y = map_y - self.mapa_cargado.rotating_background_up_y_pos
					# Update general properties on the frame properties
					self.Update_RotBg_Properties()
					# Redraw new rotating background rotation center
					self.canvas_mapview.Show_RotBg_Rotation_Center( self.mapa_cargado )
					# Change submode to no mode
					self.current_rotbg_submode = RotBg_SubMode.no_mode
					self.window_statusbar.set_field_1("%s", _("Posicion centro de giro de fondo giratorio actualizado") )
					self.canvas_mapview.Set_Cursor_Arrow()



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


	def window_close_button_handler( self ):
		logging.debug( "Se intenta cerrar la ventana principal.")
		if self.map_loaded == True:
			if messagebox.askokcancel( _("Cerrar programa") , _("¿Realmente desea cerrar el programa?") ):
				self.window_main_editor.destroy()
		else:		# no map loaded
			self.window_main_editor.destroy()


	##############################################################################

	def NewMapButton(self):			# 17/2/2021
		if self.map_loaded == True:
			answer = tk.messagebox.askyesnocancel( _("Abrir otro mapa"), _("¿Desea abrir otro mapa?\nSe perderán las modificaciones realizadas en el mapa actual") )
			logging.debug( "Pregunta abrir otro mapa, el usuario ha respondido answer = " + str(answer) )
			if (answer is None) or (answer == False) :
				return	# Do nothing

		if self.map_loaded == True:
			# If there is a map loaded, unload it before loading the new one
			self.UnloadMap()

		# Create a new empty map
		self.mapa_cargado = rceditor_maps.Map()
		self.mapa_cargado.Initialize_New_Map_Values()
		self.loaded_map_filename = _("Sin nombre")
		# Set user interface
		self.window_main_editor.title( "RoadCoin Level Editor - " + self.loaded_map_filename )
		self.map_loaded = True
		self.EnableMenuItems_MapLoaded()
		self.window_statusbar.set_field_1("%s", _("Nuevo mapa creado") )
		logging.debug( "Representando mapa en editor... " )
		self.canvas_mapview.DrawAll( self.mapa_cargado )
		# Update properties frames
		self.Update_All_Properties()



	def LoadMapButton(self):
		if self.map_loaded == True:
			answer = tk.messagebox.askyesnocancel( _("Abrir otro mapa") , _("¿Desea abrir otro mapa?\nSe perderán las modificaciones realizadas en el mapa actual") )
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
			# aqui faltan muchas cosas mas ..../

			# Load map images
			self.canvas_mapview.Load_Images( self.mapa_cargado, self.preferences )
			logging.debug( "Representando mapa en editor... " )
			self.canvas_mapview.DrawAll( self.mapa_cargado )

			self.window_main_editor.title( "RoadCoin Level Editor - " + self.loaded_map_filename )
			self.map_loaded = True
			self.EnableMenuItems_MapLoaded()

			self.window_statusbar.set_field_1("%s %s %s", _("Mapa ") , open_map_filename , _(" cargado") )

			# Update properties frames
			self.Update_All_Properties()

		#elif isinstance( chosen_new_game_path, unicode ):
			# Note: when<type 'unicode'> # Nothing selected, Cancel clicked
		#elif isinstance( chosen_new_game_path, tuple ):
			# Note: when <type 'tuple'> # File selected, Cancel clicked
			# Note: when <type 'tuple'> # Multiple files selected, OK clicked


	def SaveMapButton(self):	# 3/1/2021
		# (TODO) PENDIENTE
		# tk.messagebox.showerror(title="AVISO", message="Funcionalidad todavia no implementada")
		# pass

		if self.map_loaded == False:
			tk.messagebox.showerror(title= _("Error") , message= _("No hay ningún mapa cargado.") )
			logging.debug( "Se ha intentado guardar un mapa sin tener un mapa abierto. No hay nada que guardar." )
			return	# Do nothing

		# Apply properties frames changes (to avoid losing "last minute" changes that may not been applied)
		self.Apply_General_Map_Changes()
		self.Apply_Image_Map_Changes()
		self.Apply_RotBg_Map_Changes()	

		# Check for map errors
		map_data_ok, error_list = self.mapa_cargado.CheckMapErrorList()
		if map_data_ok == True:
			# tk.messagebox.showinfo(title="Comprobación mapa", message="No se han encontrado errores.")
			logging.debug( "Comprobación mapa: No se han encontrado errores." )
		else:
			tk.messagebox.showerror(title= _("Comprobación mapa") , message= _("Se han encontrado los siguientes errores. \n") + error_list )
			self.window_statusbar.set_field_1("%s", _("Mapa no guardado debido a errores.") )
			return	# Do nothing

		# Let's save the map
		self.mapa_cargado.SaveFile_OverwriteAll( self.loaded_map_filename )
		logging.debug( "Guardando mapa " + self.loaded_map_filename )
		self.window_statusbar.set_field_1("%s %s %s", _("Mapa ") , self.loaded_map_filename , _(" guardado.") )



	def SaveMapAsButton(self):	# 3/1/2021
		if self.map_loaded == False:
			tk.messagebox.showerror(title= _("Error"), message= _("No hay ningún mapa cargado.") )
			logging.debug( "Se ha intentado guardar un mapa sin tener un mapa abierto. No hay nada que guardar." )
			return	# Do nothing

		# Apply properties frames changes (to avoid losing "last minute" changes that may not been applied) (29/3/2021)
		self.Apply_General_Map_Changes()
		self.Apply_Image_Map_Changes()
		self.Apply_RotBg_Map_Changes()

		# Check for map errors
		map_data_ok, error_list = self.mapa_cargado.CheckMapErrorList()
		if map_data_ok == True:
			# tk.messagebox.showinfo(title="Comprobación mapa", message="No se han encontrado errores.")
			logging.debug( "Comprobación mapa: No se han encontrado errores." )
		else:
			tk.messagebox.showerror(title= _("Comprobación mapa") , message= _("Se han encontrado los siguientes errores. \n")  + error_list )
			self.window_statusbar.set_field_1("%s", _("Mapa no guardado debido a errores.") )
			return	# Do nothing


		save_map_filename = filedialog.asksaveasfilename(initialdir = self.preferences.GamePath, title = "Select file",filetypes = (("all files","*"),("all files with ext","*.*")))
		# Manage the user file selection
		if isinstance( save_map_filename, str ) and (save_map_filename != "") :
			# Note: when <type 'str'> # File selected, OK clicked
			
			# Let's save the map
			self.mapa_cargado.SaveFile_OverwriteAll( save_map_filename )
			logging.debug( "Guardando mapa " + save_map_filename )
			self.window_statusbar.set_field_1("%s %s %s", _("Mapa ") , save_map_filename , _(" guardado.") )

			# Set the open file name to the new file saved
			self.loaded_map_filename = save_map_filename
			self.window_main_editor.title( "RoadCoin Level Editor - " + self.loaded_map_filename )


		#elif isinstance( chosen_new_game_path, unicode ):
			# Note: when<type 'unicode'> # Nothing selected, Cancel clicked
		#elif isinstance( chosen_new_game_path, tuple ):
			# Note: when <type 'tuple'> # File selected, Cancel clicked
			# Note: when <type 'tuple'> # Multiple files selected, OK clicked


	def CloseMapButton(self):
		answer = tk.messagebox.askyesnocancel( _("Cerrar mapa") , _("¿Desea cerrar el mapa?") )
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
		self.window_statusbar.set_field_1("%s", _("Mapa cerrado") )


	def ShowPreferencesWindowButton(self):
		logging.debug( "Abriendo ventana preferencias" )
		self.pref_window = rceditor_preferences.PreferencesWindow( master = self.window_main_editor,  preferences=self.preferences )
		# Wait until the preferences window has been closed
		self.window_main_editor.wait_window(self.pref_window.PrefWindow)
		# Redraw everything
		if self.map_loaded == True:
			self.canvas_mapview.DrawAll( self.mapa_cargado )

	def AboutWindowButton(self):
		logging.debug( "Abriendo ventana acerca de" )
		self.about_window = rceditor_help.AboutWindow( master = self.window_main_editor )


	def RedrawAllButton(self):
		self.canvas_mapview.DrawAll( self.mapa_cargado )


	def GoTo_Origin(self):
		self.canvas_mapview.GoTo_Origin()
		# self.canvas_mapview.zoomlevel = 1.0
		self.SetZoomLevel( 1.0 )
		self.canvas_mapview.DrawAll( self.mapa_cargado )


	def ChangeZoomLevel(self, zoom_increment ):
		if self.canvas_mapview.zoomlevel + zoom_increment > 0.01:
			self.window_statusbar.set_field_1("%s", _("Aplicando zoom, espere por favor") )
			self.canvas_mapview.zoomlevel += zoom_increment
			self.canvas_mapview.DrawAll( self.mapa_cargado )
			self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
			logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (incrementado)" )
			self.window_statusbar.set_field_1("%s %f %s", "Zoom ", self.canvas_mapview.zoomlevel , _(" aplicado. Listo") )
		else:
			logging.debug("Ya estamos en el minimo zoom, no se cambia")
			self.window_statusbar.set_field_1("%s", _("Zoom minimo alcanzado") )

	def SetZoomLevel(self, zoomlevel):
		self.window_statusbar.set_field_1("%s", _("Aplicando zoom, espere por favor") )
		self.canvas_mapview.zoomlevel = zoomlevel
		self.canvas_mapview.DrawAll( self.mapa_cargado )
		self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
		logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (ajustado)" )
		self.window_statusbar.set_field_1("%s %f %s", "Zoom ", self.canvas_mapview.zoomlevel , _(" aplicado. Listo") )


	def Unselect_All( self ):
		self.UnSelect_Segment()
		self.UnSelect_Bumper()
		self.UnSelect_RACCZ()
		self.canvas_mapview.UnHighlight_All()



	def Update_General_Properties( self ):
		if self.map_loaded == True:
			# This function updates the properties frame on the right, for the general mode
			logging.debug( "Se ha llamado a la funcion Update_General_Properties, se actualiza el frame de propiedades")
			# Write name and description
			self.property_gen_map_name.set_value( self.mapa_cargado.map_name )
			self.property_gen_description.set_value( self.mapa_cargado.map_description )
			# Write rotation type
			self.property_gen_rot_type_variable.set( self.property_gen_rot_type_choices  [ self.mapa_cargado.rotation_type ] )
			# Write rotation center
			if self.mapa_cargado.rotation_center is not None:
				self.property_gen_rot_center_x.set_value( self.mapa_cargado.rotation_center.x )
				self.property_gen_rot_center_y.set_value( self.mapa_cargado.rotation_center.y )
			# Write maximum angle
			self.property_gen_max_angle.set_value( self.mapa_cargado.max_angle )
			# Write coin start position		
			self.property_gen_coin_start_pos_x.set_value( self.mapa_cargado.coin_starting_point.x )
			self.property_gen_coin_start_pos_y.set_value( self.mapa_cargado.coin_starting_point.y )
			# Write gravity
			self.property_gen_gravity.set_value( self.mapa_cargado.gravity )
			# Write scale (this parameter is optional)
			if self.mapa_cargado.scale is not None:
				self.property_gen_scale.set_value( self.mapa_cargado.scale )
			else:
				self.property_gen_scale.set_value( "" )
			# Write music path
			self.property_gen_music_path.set_value( self.mapa_cargado.music_path )
			# Write timeout (this parameter is optional)
			if self.mapa_cargado.countdown_time is not None:
				self.property_gen_timeout.set_value( self.mapa_cargado.countdown_time )
			else:
				self.property_gen_timeout.set_value( "" )

		else:
			logging.debug( "Se ha llamado a la funcion Update_General_Properties, el mapa no estaba cargado, no se ha hecho nada")


	def Apply_General_Map_Changes( self ):
		# When some values are changed in the properties frame, this function applies the changes to the map general data
		# Only to be taken into account in the general mode
		if self.current_mode == Mode.general:
			logging.debug( "Funcion Apply_General_Map_Changes llamada, se intentan aplicar los cambios al mapa." )
			try:
				# Get name and description
				self.mapa_cargado.map_name = self.property_gen_map_name.get_value_string() 
				self.mapa_cargado.map_description = self.property_gen_description.get_value_string()
				# Get rotation type
				read_rot_type = self.property_gen_rot_type_variable.get()
				for type_num, rot_type_to_compare in enumerate(self.property_gen_rot_type_choices, start=0) :
					if read_rot_type == rot_type_to_compare:
						self.mapa_cargado.rotation_type = type_num
						break	# Exit for
				# Get rotation center
				self.mapa_cargado.rotation_center.x = float(  self.property_gen_rot_center_x.get_value_string()  )
				self.mapa_cargado.rotation_center.y = float(  self.property_gen_rot_center_y.get_value_string()  )
				# Get maximum angle
				self.mapa_cargado.max_angle = float(  self.property_gen_max_angle.get_value_string()  )
				# Get coin start position
				self.mapa_cargado.coin_starting_point.x = float(  self.property_gen_coin_start_pos_x.get_value_string()  )
				self.mapa_cargado.coin_starting_point.y = float(  self.property_gen_coin_start_pos_y.get_value_string()  )
				# Draw (or redraw) coin start position
				self.canvas_mapview.Show_Coin_Start_Position( self.mapa_cargado )
				# Get gravity
				self.mapa_cargado.gravity = float(  self.property_gen_gravity.get_value_string()  )
				# Get scale (this parameter is optional)
				if self.property_gen_scale.get_value_string().strip() != "" :
					self.mapa_cargado.scale = float(  self.property_gen_scale.get_value_string()  )
				else:
					self.mapa_cargado.scale = None
				# Get music path
				self.mapa_cargado.music_path = self.property_gen_music_path.get_value_string()
				# Write timeout
				if self.property_gen_timeout.get_value_string().strip() != "" :
					self.mapa_cargado.countdown_time = int(  self.property_gen_timeout.get_value_string()  )
				else:
					self.mapa_cargado.countdown_time = None

			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_General_Map_Changes llamada, pero en el modo incorrecto. No se hace nada." )



	def Update_Image_Properties( self ):
		if self.map_loaded == True:
			# This function updates the properties frame on the right, for the image mode
			logging.debug( "Se ha llamado a la funcion Update_Image_Properties, se actualiza el frame de propiedades")
			# Write coin image path
			self.property_img_coin_path.set_value( self.mapa_cargado.coin_image_path )
			# Write background image path
			self.property_img_background_path.set_value( self.mapa_cargado.fixed_background_path )
			# Write no-rotation coin status 
			if self.mapa_cargado.coin_does_not_rotate is not None:
				if self.mapa_cargado.coin_does_not_rotate == True:
					self.property_img_norot_coin.select()
				else:
					self.property_img_norot_coin.deselect()
			else:	# it is None
				self.property_img_norot_coin.deselect()	

			# Write wall segment image path
			self.property_img_wall_segm_path.set_value( self.mapa_cargado.wall_segment_image_path )
			# Write goal segment image path
			self.property_img_goal_segm_path.set_value( self.mapa_cargado.goal_segment_image_path )
			# Write death segment image path
			self.property_img_death_segm_path.set_value( self.mapa_cargado.death_segment_image_path )
			# Write map description image for the menu
			self.property_img_description_path.set_value( self.mapa_cargado.description_image_path )
		else:
			logging.debug( "Se ha llamado a la funcion Update_Image_Properties, el mapa no estaba cargado, no se ha hecho nada")


	def Apply_Image_Map_Changes( self ):
		# When some values are changed in the properties frame, this function applies the changes to the map images data
		# Only to be taken into account in the image mode
		if self.current_mode == Mode.images:
			logging.debug( "Funcion Apply_Image_Map_Changes llamada, se intentan aplicar los cambios al mapa." )
			try:
				# Get coin image path
				self.mapa_cargado.coin_image_path = self.property_img_coin_path.get_value_string()
				# Get background image path
				self.mapa_cargado.fixed_background_path = self.property_img_background_path.get_value_string()
				# Get no-rotation coin status
				self.mapa_cargado.coin_does_not_rotate = self.property_img_norot_coin_variable.get()  
				# Get wall segment image path
				self.mapa_cargado.wall_segment_image_path = self.property_img_wall_segm_path.get_value_string()
				# Get goal segment image path
				self.mapa_cargado.goal_segment_image_path = self.property_img_goal_segm_path.get_value_string()
				# Get death segment image path
				self.mapa_cargado.death_segment_image_path = self.property_img_death_segm_path.get_value_string()
				# Get map description image for the menu
				self.mapa_cargado.description_image_path = self.property_img_description_path.get_value_string()

			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Image_Map_Changes llamada, pero en el modo incorrecto. No se hace nada." )


	def Update_RotBg_Properties( self ):
		if self.map_loaded == True:
			# This function updates the properties frame on the right, for the rotation background mode
			logging.debug( "Se ha llamado a la funcion Update_RotBg_Properties, se actualiza el frame de propiedades")
			# Write whether the rotating background exists or not 
			if self.mapa_cargado.rotating_background is not None:
				if self.mapa_cargado.rotating_background == True:
					self.property_rotbg_exists.select()
				else:
					self.property_rotbg_exists.deselect()
			else:	# it is None
				self.property_img_norot_coin.deselect()	

			# The following only are taken into account when there is a rotating background
			if self.mapa_cargado.rotating_background is not None:
				if self.mapa_cargado.rotating_background == True:
					# Write rotating background image path
					self.property_rotbg_path.set_value( self.mapa_cargado.rotating_background_path )
					# Write rotating background position coordinates
					self.property_rotbg_left_x.set_value(  self.mapa_cargado.rotating_background_left_x_pos  )
					self.property_rotbg_up_y.set_value(  self.mapa_cargado.rotating_background_up_y_pos  )
					self.property_rotbg_right_x.set_value(  self.mapa_cargado.rotating_background_right_x_pos  )
					self.property_rotbg_down_y.set_value(  self.mapa_cargado.rotating_background_down_y_pos  )
					# Write rotating background rotation center
					self.property_rotbg_center_x.set_value(  self.mapa_cargado.rotating_background_center.x  )
					self.property_rotbg_center_y.set_value(  self.mapa_cargado.rotating_background_center.y  )

		else:
			logging.debug( "Se ha llamado a la funcion Update_Image_Properties, el mapa no estaba cargado, no se ha hecho nada")


	def Apply_RotBg_Map_Changes( self ):
		# When some values are changed in the properties frame, this function applies the changes to the rotating background data
		# Only to be taken into account in the rotating background mode
		if self.current_mode == Mode.rot_bg:
			logging.debug( "Funcion Apply_RotBg_Map_Changes llamada, se intentan aplicar los cambios al mapa." )
			try:
				# Get whether the rotating background exists or not 
				self.mapa_cargado.rotating_background = self.property_rotbg_exists_variable.get()
				# Get rotating background image path
				if self.property_rotbg_path.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_path = self.property_rotbg_path.get_value_string()
				else:
					self.mapa_cargado.rotating_background_path = None
				# Get rotating background position coordinates
				if self.property_rotbg_left_x.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_left_x_pos = int(  self.property_rotbg_left_x.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_left_x_pos = None

				if self.property_rotbg_up_y.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_up_y_pos = int(  self.property_rotbg_up_y.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_up_y_pos = None

				if self.property_rotbg_right_x.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_right_x_pos = int(  self.property_rotbg_right_x.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_right_x_pos = None

				if self.property_rotbg_down_y.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_down_y_pos = int(  self.property_rotbg_down_y.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_down_y_pos = None
				# Get rotating background rotation center
				if self.property_rotbg_center_x.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_center.x = float(  self.property_rotbg_center_x.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_center.x = None

				if self.property_rotbg_center_y.get_value_string().strip() != "" :
					self.mapa_cargado.rotating_background_center.y = float(  self.property_rotbg_center_y.get_value_string()  )
				else:
					self.mapa_cargado.rotating_background_center.y = None
				# Update canvas display - Redraw rotating background (17/2/2021)
				self.canvas_mapview.Load_Images( self.mapa_cargado, self.preferences )
				self.canvas_mapview.DrawAll( self.mapa_cargado )
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ")  + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_RotBg_Map_Changes llamada, pero en el modo incorrecto. No se hace nada." )


	def Update_Selected_Segment_Properties( self, segm_number ):
		# When a segment is selected, this function updates the properties frame on the right
		# Write number and coords
		self.property_segm_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_segm_number.set_value( segm_number )
		self.property_segm_number.config_entry( state='readonly' )
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
		# Enable erase button (6/11/2020)
		self.button_del_segm.config(state="normal")


	def Apply_Selected_Segment_Changes( self ):
		# When a segment is selected, and some values are changed in the properties frame, this function applies the changes to the "segment dictionary"
		# Only to be taken into account in the segment edit mode
		if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.edit:
			logging.debug( "Funcion Apply_Selected_Segment_Changes llamada, se intentan aplicar los cambios al diccionario." )
			try:
				# Read selected segment
				segm_number = int( self.property_segm_number.get_value_string() )
				# Get segment coordinates
				self.mapa_cargado.segment_dict.get(segm_number).start.x = float( self.property_segm_start_x.get_value_string() )
				self.mapa_cargado.segment_dict.get(segm_number).start.y = float( self.property_segm_start_y.get_value_string() )
				self.mapa_cargado.segment_dict.get(segm_number).end.x = float( self.property_segm_end_x.get_value_string() )
				self.mapa_cargado.segment_dict.get(segm_number).end.y = float( self.property_segm_end_y.get_value_string() )
				# Get segment type
				read_segm_type = self.property_segm_type_variable.get()
				for type_num, segm_type_to_compare in enumerate(self.property_segm_type_choices, start=0) :
					if read_segm_type == segm_type_to_compare:
						self.mapa_cargado.segment_dict.get(segm_number).segm_type = type_num
						break	# Exit for
				# Get segment visibility
				self.mapa_cargado.segment_dict.get(segm_number).invisible = self.property_segm_invis_variable.get()  
				# Update canvas display
				self.canvas_mapview.Update_Segments_Display( [segm_number], self.mapa_cargado )
				self.canvas_mapview.Highlight_Segments( [segm_number] )		# Type cast into list. After update, we need to highlight again
				self.Update_Selected_Segment_Properties( segm_number )
				logging.debug( "Modificaciones segmento leidas: segm_num = " + str(segm_number) + \
						", start: x= " + str(self.mapa_cargado.segment_dict.get(segm_number).start.x) + \
						", y= " + str( self.mapa_cargado.segment_dict.get(segm_number).start.y ) + \
						", end: x= " + str(self.mapa_cargado.segment_dict.get(segm_number).end.x) + \
						", y= " + str( self.mapa_cargado.segment_dict.get(segm_number).end.y) + \
						". Tipo = " + str( type_num ) + "(" + read_segm_type + ")" + \
						". Invisible = " + str( self.mapa_cargado.segment_dict.get(segm_number).invisible ) )


				### Redraw segment table (if the table is displayed)  # 16/3/2021
				if self.segment_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de segmentos que debe actualizar el segmento numero " + str(segm_number) )
					self.segment_table.update_table_row_values_from_map( segm_number )

			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Selected_Segment_Changes llamada, pero en el modo incorrecto. No se hace nada." )

		
	def UnSelect_Segment( self ):
		# When a segment was selected, and we want to deselect it, this function updates the properties frame on the right
		logging.debug( "Segmento " +  self.property_segm_number.get_value_string() + " deseleccionado." )
		# Erase number and coords
		self.property_segm_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_segm_number.set_value( "" )
		self.property_segm_number.config_entry( state='readonly' )
		self.property_segm_start_x.set_value( "" ) 
		self.property_segm_start_y.set_value( "" )
		self.property_segm_end_x.set_value( "" ) 
		self.property_segm_end_y.set_value( "" ) 
		# Erase segment type
		self.property_segm_type_variable.set( "" )
		# Erase segment visibility
		self.property_segm_invis.deselect()
		# Disable erase button (6/11/2020)
		self.button_del_segm.config(state="disabled")

	def Delete_Selected_Segment( self ):   #  (6/11/2020)
		# When a segment is selected and the delete button is pressed, this function makes the actions to delete it.
		if self.map_loaded == True:
			selected_segment =  self.property_segm_number.get_value_string()
			if ( selected_segment != "" ) and ( selected_segment.isnumeric() == True ):
				answer = tk.messagebox.askyesnocancel( _("Eliminar segmento"), _("¿Desea eliminar el segmento numero ") + selected_segment + "?")
				logging.debug( "Pregunta eliminar segmento, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeleteSegment( int(selected_segment) )
				self.mapa_cargado.Segments_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", _("Segmento ") , selected_segment , _(" borrado") )
				
				### Redraw segment table (if the table is displayed)  # 16/3/2021
				if self.segment_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de segmentos que debe actualizarse." )
					self.segment_table.update_table_from_map_editor()

			else:
				tk.messagebox.showerror(title= _("Error") , message= _("El numero de segmento seleccionado (") + selected_segment + _(") no es valido." ) )
				logging.debug( "Error de programación: El numero de segmento seleccionado (" + selected_segment + ") no es valido." )
		else:
			tk.messagebox.showerror(title=_("Error"), message= _("No hay ningún mapa cargado.") )


	def Update_Selected_Bumper_Properties( self, bumper_number ):
		# When a pinball bumper is selected, this function updates the properties frame on the right
		# Write number and coords
		self.property_bumper_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_bumper_number.set_value( bumper_number )
		self.property_bumper_number.config_entry( state='readonly' )
		self.property_bumper_center_x.set_value(  self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.x  ) 
		self.property_bumper_center_y.set_value(  self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.y  )
		# Write radius
		self.property_bumper_radius.set_value(  self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).radius  ) 
		# Write exit speed
		self.property_bumper_speed.set_value(  self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).exit_speed  ) 
		# Enable erase button (8/11/2020)
		self.button_del_bumper.config(state="normal")


	def Apply_Selected_Bumper_Changes( self ):
		# When a pinball bumper is selected, and some values are changed in the properties frame, this function applies the changes to the "pinball bumper dictionary"
		# Only to be taken into account in the bumper edit mode
		if self.current_mode == Mode.bumper and self.current_bumper_submode == Bumper_SubMode.edit:
			logging.debug( "Funcion Apply_Selected_Bumper_Changes llamada, se intentan aplicar los cambios al diccionario." )
			try:
				# Read selected bumper
				bumper_number = int( self.property_bumper_number.get_value_string() )
				# Get bumper coordinates
				self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.x = float( self.property_bumper_center_x.get_value_string() )
				self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.y = float( self.property_bumper_center_y.get_value_string() )
				# Get bumper radius
				self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).radius = float( self.property_bumper_radius.get_value_string() )
				# Get bumper exit speed
				self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).exit_speed = float( self.property_bumper_speed.get_value_string() )
				# Update canvas display
				self.canvas_mapview.Update_Bumpers_Display( [bumper_number], self.mapa_cargado )
				self.canvas_mapview.Highlight_Bumpers( [bumper_number] )		# Type cast into list. After update, we need to highlight again
				self.Update_Selected_Bumper_Properties( bumper_number )
				logging.debug( "Modificaciones bumper leidas: bumper_num = " + str(bumper_number) + \
						", centro: x= " + str(self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.x) + \
						", y= " + str( self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).center.y ) + \
						", radio= " + str(self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).radius) + \
						", vel_salida= " + str( self.mapa_cargado.pinball_bumpers_dict.get(bumper_number).exit_speed) )

				### Redraw bumper table (if the table is displayed)  # 18/3/2021
				if self.bumper_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de bumpers que debe actualizar el bumper numero " + str(bumper_number) )
					self.bumper_table.update_table_row_values_from_map( bumper_number )


			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Selected_Bumper_Changes llamada, pero en el modo incorrecto. No se hace nada." )


	def UnSelect_Bumper( self ):
		# When a bumper was selected, and we want to deselect it, this function updates the properties frame on the right
		logging.debug( "Bumper " +  self.property_bumper_number.get_value_string() + " deseleccionado." )
		# Erase number and coords
		self.property_bumper_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_bumper_number.set_value( "" )
		self.property_bumper_number.config_entry( state='readonly' )
		self.property_bumper_center_x.set_value( "" ) 
		self.property_bumper_center_y.set_value( "" )
		self.property_bumper_radius.set_value( "" ) 
		self.property_bumper_speed.set_value( "" ) 
		# Disable erase button (8/11/2020)
		self.button_del_bumper.config(state="disabled")

	def Delete_Selected_Bumper( self ):   #  (8/11/2020)
		# When a bumper is selected and the delete button is pressed, this function makes the actions to delete it.
		if self.map_loaded == True:
			selected_bumper =  self.property_bumper_number.get_value_string()
			if ( selected_bumper != "" ) and ( selected_bumper.isnumeric() == True ):
				answer = tk.messagebox.askyesnocancel( _("Eliminar bumper") , _("¿Desea eliminar el bumper numero ")  + selected_bumper + "?")
				logging.debug( "Pregunta eliminar bumper, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeletePinballBumper( int(selected_bumper) )
				self.mapa_cargado.Bumpers_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", _("Bumper ") , selected_bumper , _(" borrado") )

				### Redraw bumper table (if the table is displayed)  # 18/3/2021
				if self.bumper_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de bumpers que debe actualizarse." )
					self.bumper_table.update_table_from_map_editor()
			else:
				tk.messagebox.showerror(title= _("Error") , message= _("El numero de bumper seleccionado (") + selected_bumper + _(") no es valido.") )
				logging.dialog( "Error de programación: El numero de bumper seleccionado (" + selected_bumper + ") no es valido." )
		else:
			tk.messagebox.showerror(title= _("Error") , message= _("No hay ningún mapa cargado.") )

	def Update_Selected_RACCZ_Properties( self, raccz_number ):
		# When a raccz is selected, this function updates the properties frame on the right
		# Write number and coords
		self.property_raccz_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_raccz_number.set_value( raccz_number )
		self.property_raccz_number.config_entry( state='readonly' )
		self.property_raccz_center_x.set_value(  self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.x  ) 
		self.property_raccz_center_y.set_value(  self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.y  )
		# Write radius
		self.property_raccz_radius.set_value(  self.mapa_cargado.dict_round_acel_zones.get(raccz_number).radius  ) 
		# Write angle
		self.property_raccz_angle.set_value(  self.mapa_cargado.dict_round_acel_zones.get(raccz_number).angle  ) 
		# Write acceleration
		self.property_raccz_accel.set_value(  self.mapa_cargado.dict_round_acel_zones.get(raccz_number).acceleration  ) 
		# Write segment visibility
		if self.mapa_cargado.dict_round_acel_zones.get(raccz_number).invisible == True:
			self.property_raccz_invis.select()
		else:
			self.property_raccz_invis.deselect()
		# Enable erase button (8/11/2020)
		self.button_del_raccz.config(state="normal")
		


	def Apply_Selected_RACCZ_Changes( self ):
		# When a raccz is selected, and some values are changed in the properties frame, this function applies the changes to the "raccz dictionary"
		# Only to be taken into account in the raccz edit mode
		if self.current_mode == Mode.round_accel_zone and self.current_raccz_submode == RACCZ_SubMode.edit:
			logging.debug( "Funcion Apply_Selected_RACCZ_Changes llamada, se intentan aplicar los cambios al diccionario." )
			try:
				# Read selected raccz
				raccz_number = int( self.property_raccz_number.get_value_string() )
				# Get raccz coordinates
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.x = float( self.property_raccz_center_x.get_value_string() )
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.y = float( self.property_raccz_center_y.get_value_string() )
				# Get radius
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).radius = float( self.property_raccz_radius.get_value_string() )
				# Get angle coordinates
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).angle = float( self.property_raccz_angle.get_value_string() )
				# Get accel
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).acceleration = float( self.property_raccz_accel.get_value_string() )
				# Get raccz visibility
				self.mapa_cargado.dict_round_acel_zones.get(raccz_number).invisible = self.property_raccz_invis_variable.get()  
				# Update canvas display
				self.canvas_mapview.Update_RACCZ_Display( [raccz_number], self.mapa_cargado )
				self.canvas_mapview.Highlight_RACCZ( [raccz_number] )		# Type cast into list. After update, we need to highlight again
				self.Update_Selected_RACCZ_Properties( raccz_number )
				logging.debug( "Modificaciones zona de aceleracion circular leidas: raccz_num = " + str(raccz_number) + \
						", centro: x= " + str(self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.x) + \
						", y= " + str( self.mapa_cargado.dict_round_acel_zones.get(raccz_number).center.y ) + \
						", radio= " + str(self.mapa_cargado.dict_round_acel_zones.get(raccz_number).radius) + \
						", angulo= " + str(self.mapa_cargado.dict_round_acel_zones.get(raccz_number).angle) + \
						", aceleracion= " + str( self.mapa_cargado.dict_round_acel_zones.get(raccz_number).acceleration) + \
						". Invisible = " + str( self.mapa_cargado.dict_round_acel_zones.get(raccz_number).invisible ) )

				### Redraw raccz table (if the table is displayed)  # 16/3/2021
				if self.RACCZ_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de zonas de aceleracion circular que debe actualizar el segmento numero " + str(raccz_number) )
					self.RACCZ_table.update_table_row_values_from_map( segm_number )

			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title= _("Error") , message= _("Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: ") + str( sys.exc_info()[0] ) + "\n" + str(e) )
		else:
			logging.debug( "Funcion Apply_Selected_RACCZ_Changes llamada, pero en el modo incorrecto. No se hace nada." )


	def UnSelect_RACCZ( self ):
		# When a raccz was selected, and we want to deselect it, this function updates the properties frame on the right
		logging.debug( "Zona de aceleracion circular " +  self.property_raccz_number.get_value_string() + " deseleccionado." )
		# Erase number and coords
		self.property_raccz_number.config_entry( state='normal' )	# Note: When entrybox is disabled or readonly, insert and delete are ignored
		self.property_raccz_number.set_value( "" )
		self.property_raccz_number.config_entry( state='readonly' )
		self.property_raccz_center_x.set_value( "" ) 
		self.property_raccz_center_y.set_value( "" )
		# Erase radius
		self.property_raccz_radius.set_value( "" ) 
		# Erase angle
		self.property_raccz_angle.set_value( "" ) 
		# Erase acceleration
		self.property_raccz_accel.set_value( "" ) 
		# Erase segment visibility
		self.property_raccz_invis.deselect()
		# Disable erase button (8/11/2020)
		self.button_del_raccz.config(state="disabled")


	def Delete_Selected_RACCZ( self ):   #  (8/11/2020)
		# When a RACCZ is selected and the delete button is pressed, this function makes the actions to delete it.
		if self.map_loaded == True:
			selected_raccz =  self.property_raccz_number.get_value_string()
			if ( selected_raccz != "" ) and ( selected_raccz.isnumeric() == True ):
				answer = tk.messagebox.askyesnocancel( _("Eliminar zona acel circular"), _("¿Desea eliminar la zona de aceleracion circular numero ") + selected_raccz + "?")
				logging.debug( "Pregunta eliminar zona de aceleracion circular, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeleteRACCZ( int(selected_raccz) )
				self.mapa_cargado.RACCZ_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", "Zona acel circ ", selected_raccz , " borrada" )

				### Redraw raccz table (if the table is displayed)  # 21/3/2021
				if self.RACCZ_table is not None:
					logging.debug( "La interfaz principal indica a la tabla de zonas de aceleracion circular que debe actualizarse." )
					self.RACCZ_table.update_table_from_map_editor()

			else:
				tk.messagebox.showerror(title= _("Error") , message= _("El numero de zona aceleracion circular seleccionado (") + selected_raccz + _(") no es valido.") )
				logging.dialog( "Error de programación: El numero de zona de aceleracion circular seleccionado (" + selected_raccz + ") no es valido." )
		else:
			tk.messagebox.showerror(title= _("Error") , message= _("No hay ningún mapa cargado.") )


	def Toggle_Show_Hide_Segment_Table( self ):
		if self.map_loaded == True:
			if self.segment_table is None:		# Segment table is not open (the object does not exist)
				self.segment_table = rceditor_table_segm.Segment_Table_Window( master = self.window_main_editor, Map = self.mapa_cargado , owner=self )
			else:					# Segment table is already open
				self.segment_table.SegmentTableWindow.destroy()
				del self.segment_table
				self.segment_table = None


	def Toggle_Show_Hide_Bumper_Table( self ):
		# PROVISIONAL, DEBE SER PROBADO (TODO)
		if self.map_loaded == True:
			if self.bumper_table is None:		# Bumper table is not open (the object does not exist)
				self.bumper_table = rceditor_table_bumper.Bumper_Table_Window( master = self.window_main_editor, Map = self.mapa_cargado , owner=self )
			else:					# Bumper table is already open
				self.bumper_table.BumperTableWindow.destroy()
				del self.bumper_table
				self.bumper_table = None


	def Toggle_Show_Hide_RACCZ_Table( self ):
		# PROVISIONAL, DEBE SER PROBADO (TODO)
		if self.map_loaded == True:
			if self.RACCZ_table is None:		# Segment table is not open (the object does not exist)
				self.RACCZ_table = rceditor_table_raccz.RACCZ_Table_Window( master = self.window_main_editor, Map = self.mapa_cargado , owner=self )
			else:					# Segment table is already open
				self.RACCZ_table.RACCZTableWindow.destroy()
				del self.RACCZ_table
				self.RACCZ_table = None


	def General_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función General_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.general:
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_General_Map_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.


	def General_Property_OPTIONAL_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		# Used when the parameter is OPTIONAL
		logging.debug( "Llamada a función General_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.general:
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_General_Map_Changes()
					return(True)
				elif text_after_change.strip() == "":	# String is empty
					logging.debug("El nuevo texto es una cadena vacia.")
					self.Apply_General_Map_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.


	def General_Property_OptionMenu_Click_Callback( self, ChosenOption ):
		# This function will be called when a OptionMenu on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función General_Property_OptionMenu_Click_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", opcion elegida: " + ChosenOption )
		if self.map_loaded == True:
			if self.current_mode == Mode.general:
				self.Apply_General_Map_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def General_Property_String_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función General_Property_String_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.general:
				if text_after_change == text_before_change:
					logging.debug("El texto ha cambiado.")
					self.Apply_General_Map_Changes()
					return(True)
				else:
					logging.debug("El texto no ha cambiado, no se hace nada.")
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.


	def Image_Property_String_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Image_Property_String_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.images:
				if text_after_change == text_before_change:
					logging.debug("El texto ha cambiado.")
					self.Apply_Image_Map_Changes()
					return(True)
				else:
					logging.debug("El texto no ha cambiado, no se hace nada.")
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.

	def Image_Property_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Image_Property_Checkbox_Click_Callback: Modo = " + mode_names.get( self.current_mode ) )
		if self.map_loaded == True:
			if self.current_mode == Mode.images:
				self.Apply_Image_Map_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def RotBg_Property_String_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función RotBg_Property_String_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.rot_bg:
				if text_after_change == text_before_change:
					logging.debug("El texto ha cambiado.")
					self.Apply_RotBg_Map_Changes()
					return(True)
				else:
					logging.debug("El texto no ha cambiado, no se hace nada.")
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.



	def RotBg_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función RotBg_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.rot_bg:
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_RotBg_Map_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.

	def RotBg_Property_OPTIONAL_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		# Used when the parameter is OPTIONAL
		logging.debug( "Llamada a función RotBg_Property_OPTIONAL_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.rot_bg:
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_RotBg_Map_Changes()
					return(True)
				elif text_after_change.strip() == "":	# String is empty
					logging.debug("El nuevo texto es una cadena vacia.")
					self.Apply_RotBg_Map_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
					return(False)
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.


	def RotBg_Property_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función RotBg_Property_Checkbox_Click_Callback: Modo = " + mode_names.get( self.current_mode ) )
		if self.map_loaded == True:
			if self.current_mode == Mode.rot_bg:
				self.Apply_RotBg_Map_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def Segment_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.segment:
				selected_segment =  self.property_segm_number.get_value_string()
				if ( selected_segment != "" ) and ( selected_segment.isnumeric() == True ):		# Check if a segment is selected
					if isFloat(text_after_change) == True:
						logging.debug("El nuevo texto es un numero.")
						self.Apply_Selected_Segment_Changes()
						return(True)
					else:
						logging.debug("El nuevo texto no es un numero.")
						tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
						return(False)
				else:
					logging.debug("Ningun segmento seleccionado. No se hace nada.")
					return(False)				
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.
	

	def Bumper_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Bumper_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.bumper:
				selected_bumper =  self.property_bumper_number.get_value_string()
				if ( selected_bumper != "" ) and ( selected_bumper.isnumeric() == True ):		# Check if a bumper is selected
					if isFloat(text_after_change) == True:
						logging.debug("El nuevo texto es un numero.")
						self.Apply_Selected_Bumper_Changes()
						return(True)
					else:
						logging.debug("El nuevo texto no es un numero.")
						tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
						return(False)
				else:
					logging.debug("Ningun bumper seleccionado. No se hace nada.")
					return(False)						
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.


	def RACCZ_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Bumper_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.round_accel_zone:
				selected_raccz =  self.property_raccz_number.get_value_string()
				if ( selected_raccz != "" ) and ( selected_raccz.isnumeric() == True ):		# Check if a RACCZ is selected
					if isFloat(text_after_change) == True:
						logging.debug("El nuevo texto es un numero.")
						self.Apply_Selected_RACCZ_Changes()
						return(True)
					else:
						logging.debug("El nuevo texto no es un numero.")
						tk.messagebox.showerror(title= _("Error") , message= _("Valor no válido, no es un número. No se tienen en cuenta las modificaciones.") )
						return(False)
				else:
					logging.debug("Ninguna zona de aceleracion circular seleccionada. No se hace nada.")
					return(False)					
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")
			return(False)
		# Note: This validation function must always return true (validation OK) or false (validation NOT OK)
		# This only restores the original value in the 'key' validation mode. In the 'focusout' mode, the wrong value persists.
		# Warning: In case nothing is returned, then this function will never be called again (???) and the program will be broken.

	
	def Segment_Property_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Property_Checkbox_Click_Callback: Modo = " + mode_names.get( self.current_mode ) )
		if self.map_loaded == True:
			if self.current_mode == Mode.segment:
				self.Apply_Selected_Segment_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def Segment_Property_OptionMenu_Click_Callback( self, ChosenOption ):
		# This function will be called when a OptionMenu on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Property_OptionMenu_Click_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", opcion elegida: " + ChosenOption )
		if self.map_loaded == True:
			if self.current_mode == Mode.segment:
				self.Apply_Selected_Segment_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def RACCZ_Property_Checkbox_Click_Callback( self ):
		# This function will be called when a checkbox on the properties frame is clicked (if everything is set up correctly, of course)
		logging.debug( "Llamada a función RACCZ_Property_Checkbox_Click_Callback: Modo = " + mode_names.get( self.current_mode ) )
		if self.map_loaded == True:
			if self.current_mode == Mode.round_accel_zone:
				self.Apply_Selected_RACCZ_Changes()
			else:
				logging.debug("Modo incorrecto. No se hace nada.")
				return(False)	
		else:
			logging.debug("Mapa no cargado. No se hace nada")


	def Check_Map_Data( self ):
		# For DEBUG purposes
		if self.map_loaded == True:
			map_data_ok, error_list = self.mapa_cargado.CheckMapErrorList()
			if map_data_ok == True:
				tk.messagebox.showinfo(title= _("Comprobación mapa") , message= _("No se han encontrado errores.") )
			else:
				tk.messagebox.showerror(title= _("Comprobación mapa") , message= _("Se han encontrado los siguientes errores. \n") + error_list )		
		else:
			tk.messagebox.showerror(title= _("Error") , message= _("No hay ningún mapa cargado.") )

	def ReenumerateSegments( self ):
		# For DEBUG purposes	
		if self.map_loaded == True:
			self.mapa_cargado.Segments_Reenumerate()
			self.canvas_mapview.DrawAll( self.mapa_cargado )
		else:
			tk.messagebox.showerror(title= _("Error") , message= ("No hay ningún mapa cargado.") )


	def Toggle_SnapToPoint_Segm_Button( self ):
		# This function is called every time the SnapToPoint button is pressed
		if self.snap_to_segm_point == False:
			logging.debug("Activado modo alineamiento a puntos de segmentos")
			self.snap_to_segm_point = True
			self.button_snap_point_segm.configure(bg = "green")
		else:		# True
			logging.debug("Desactivado modo alineamiento a puntos de segmentos")
			self.snap_to_segm_point = False
			self.button_snap_point_segm.configure(bg = self.orig_button_bg_color )


	def Update_All_Properties( self ):
		# This function updates all properties on the properties frame
		self.Update_General_Properties()
		self.Update_Image_Properties()
		self.Update_RotBg_Properties()
		pass	# Update_....			(TODO)


	def Choose_Coin_Starting_Point_Button_Callback( self ):
		if self.map_loaded == True:
			self.window_statusbar.set_field_1("%s", _("Seleccione punto inicial de la moneda")  )
			self.current_general_submode = General_SubMode.choose_coin_start_pos
			self.canvas_mapview.Set_Cursor_Cross()


	def Choose_Rotation_Center_Button_Callback( self ):
		if self.map_loaded == True:
			self.window_statusbar.set_field_1("%s", _("Seleccione centro de giro")  )
			self.current_general_submode = General_SubMode.choose_rotarion_center
			self.canvas_mapview.Set_Cursor_Cross()			


	def Choose_Rotating_Background_Rotation_Center_Button_Callback( self ):
		if self.map_loaded == True:
			self.window_statusbar.set_field_1("%s", _("Seleccione centro de giro del fondo giratorio") )
			self.current_rotbg_submode = RotBg_SubMode.choose_rotbg_center
			self.canvas_mapview.Set_Cursor_Cross()

