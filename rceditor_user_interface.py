
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
import rceditor_tables


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
	

##########################################################################

class RC_editor_GUI():

	current_mode = Mode.no_mode
	current_segment_submode = Segment_SubMode.no_mode
	current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start
	current_bumper_submode = Bumper_SubMode.no_mode
	current_bumper_add_stage = Bumper_Add_Stages.St0_Choose_Center
	current_raccz_submode = RACCZ_SubMode.no_mode
	current_raccz_submode = RACCZ_Add_Stages.St0_Choose_Center
	map_loaded = False
	loaded_map_filename = None
	segment_table = None
	temp_segment_data_to_create = rceditor_maps.Segment( start=rceditor_maps.Point(None,None), end=rceditor_maps.Point(None,None), segm_type=rceditor_maps.Segment_Type.wall, invisible=False)


	def __init__(self, debugmode=False ):
		logging.debug( "Cargando fichero de preferencias" )
		self.preferences = rceditor_preferences.Preferences()
		self.preferences.LoadPreferences()

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
		if debugmode==True:
			self.debugmenu = tk.Menu(self.menubar_mainmenu, tearoff=0)
			self.debugmenu.add_command(label="Verificar datos mapa", command = self.Check_Map_Data)
			self.debugmenu.add_command(label="Reenumerar segmentos", command = self.ReenumerateSegments)
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
		self.button_del_segm = tk.Button( master = self.frame_left_toolbar, text="Eliminar", image=self.img_del_segm_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_Segment )
		self.button_table_segm = tk.Button( master = self.frame_left_toolbar, text="Tabla", image=self.img_table_icon, compound=tk.LEFT, width=None, command = self.Toggle_Show_Hide_Table )
		self.button_segm4 = tk.Button( master = self.frame_left_toolbar, text="Segm4", width=6, command = do_nothing)
		self.button_segm5 = tk.Button( master = self.frame_left_toolbar, text="Segm5", width=6, command = do_nothing)
		self.button_segm6 = tk.Button( master = self.frame_left_toolbar, text="Segm6", width=6, command = do_nothing)
		self.buttons_segm_list = [ self.button_new_segm, self.button_edit_segm, self.button_del_segm, self.button_table_segm, self.button_segm4, self.button_segm5, self.button_segm6 ]
		# Bumpers mode buttons
		self.button_new_bumper = tk.Button( master = self.frame_left_toolbar, text="Nuevo", image=self.img_new_bumper_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_BumperSubMode, Bumper_SubMode.add))
		self.button_edit_bumper = tk.Button( master = self.frame_left_toolbar, text="Editar", image=self.img_edit_bumper_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_BumperSubMode, Bumper_SubMode.edit ) )
		self.button_del_bumper = tk.Button( master = self.frame_left_toolbar, text="Eliminar", image=self.img_del_bumper_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_Bumper )
		self.button_table_bumper = tk.Button( master = self.frame_left_toolbar, text="Tabla", image=self.img_table_icon, compound=tk.LEFT, width=None, command = do_nothing )
		self.buttons_bump_list = [ self.button_new_bumper, self.button_edit_bumper, self.button_del_bumper, self.button_table_bumper ]
		# RACCZ mode buttons
		self.button_new_raccz = tk.Button( master = self.frame_left_toolbar, text="Nuevo", image=self.img_new_raccz_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_RACCZSubMode, RACCZ_SubMode.add))
		self.button_edit_raccz = tk.Button( master = self.frame_left_toolbar, text="Editar", image=self.img_edit_raccz_icon, compound=tk.LEFT, width=None, command = partial(self.Reconf_UI_To_RACCZSubMode, RACCZ_SubMode.edit ) )
		self.button_del_raccz = tk.Button( master = self.frame_left_toolbar, text="Eliminar", image=self.img_del_raccz_icon, compound=tk.LEFT, width=None, state="disabled", command = self.Delete_Selected_RACCZ )
		self.button_table_raccz = tk.Button( master = self.frame_left_toolbar, text="Tabla", image=self.img_table_icon, compound=tk.LEFT, width=None, command = do_nothing )
		self.button_raccz4 = tk.Button( master = self.frame_left_toolbar, text="Raccz4", width=6, command = do_nothing)
		self.buttons_raccz_list = [ self.button_new_raccz, self.button_edit_raccz, self.button_del_raccz, self.button_table_raccz, self.button_raccz4 ]


		logging.debug( "Creando widgets del panel de propiedades para cada modo " )
		# Register validation methods
		Segment_RealNumber_Validation = self.window_main_editor.register(self.Segment_Property_RealNumber_Change_FocusOut_Validation_Callback)
		Bumper_RealNumber_Validation = self.window_main_editor.register(self.Bumper_Property_RealNumber_Change_FocusOut_Validation_Callback)
		RACCZ_RealNumber_Validation = self.window_main_editor.register(self.RACCZ_Property_RealNumber_Change_FocusOut_Validation_Callback)
		# General mode properties widgets
		self.property_gen1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 1", validatecommand=do_nothing )
		self.property_gen2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 2", validatecommand=do_nothing )
		self.property_gen3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Gen 3", validatecommand=do_nothing )
		self.properties_gen_list = [ self.property_gen1, self.property_gen2, self.property_gen3 ]
		# Image mode properties widgets
		self.property_img1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 1", validatecommand=do_nothing )
		self.property_img2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 2", validatecommand=do_nothing )
		self.property_img3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Image 3", validatecommand=do_nothing )
		self.properties_img_list = [ self.property_img1, self.property_img2, self.property_img3 ]
		# Rotating background mode properties widgets
		self.property_rotbg1 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 1", validatecommand=do_nothing )
		self.property_rotbg2 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 2", validatecommand=do_nothing )
		self.property_rotbg3 = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="rotbg 3", validatecommand=do_nothing )
		self.properties_rotbg_list = [ self.property_rotbg1, self.property_rotbg2, self.property_rotbg3 ]
		# Segment mode properties widgets
		self.property_segm_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Numero segmento:", validatecommand=do_nothing, state='readonly' )
		self.property_segm_start_label = tk.Label(master=self.frame_properties,text="Start:")
		self.property_segm_start_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_start_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_end_label = tk.Label(master=self.frame_properties,text="End:")
		self.property_segm_end_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_end_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Segment_RealNumber_Validation )
		self.property_segm_type_label = tk.Label(master=self.frame_properties, text="Tipo segmento:")
		self.property_segm_type_variable = tk.StringVar()
		self.property_segm_type_choices = [ rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.wall), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.goal), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.death), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_L), \
							rceditor_maps.Segment_Type_Names.get(rceditor_maps.Segment_Type.pinball_flipper_R)  ]
		self.property_segm_type = tk.OptionMenu( self.frame_properties, self.property_segm_type_variable, *self.property_segm_type_choices, command=self.Segment_Property_OptionMenu_Click_Callback )
		self.property_segm_invis_variable = tk.BooleanVar()
		self.property_segm_invis = tk.Checkbutton(master=self.frame_properties, text="Invisible", var=self.property_segm_invis_variable, command=self.Segment_Property_Checkbox_Click_Callback )
		self.property_segm_apply = tk.Button( master = self.frame_properties, text="Forzar aplicar cambios", command = self.Apply_Selected_Segment_Changes)
		self.properties_segm_list = [ self.property_segm_number, self.property_segm_start_label, self.property_segm_start_x, self.property_segm_start_y, self.property_segm_end_label, self.property_segm_end_x, self.property_segm_end_y, self.property_segm_type_label, self.property_segm_type, self.property_segm_type, self.property_segm_invis, self.property_segm_apply ]
		# Bumpers mode properties widgets
		self.property_bumper_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Numero bumper:", validatecommand=do_nothing, state='readonly' )
		self.property_bumper_center_label = tk.Label(master=self.frame_properties,text="Centro:")
		self.property_bumper_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_radius_label = tk.Label(master=self.frame_properties,text="Radio:")
		self.property_bumper_radius = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Radio:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_speed_label = tk.Label(master=self.frame_properties, text="Velocidad de salida:")
		self.property_bumper_speed = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="V salida:", validatecommand=Bumper_RealNumber_Validation )
		self.property_bumper_apply = tk.Button( master = self.frame_properties, text="Forzar aplicar cambios", command = self.Apply_Selected_Bumper_Changes)
		self.properties_bump_list = [ self.property_bumper_number, self.property_bumper_center_label, self.property_bumper_center_x, self.property_bumper_center_y, self.property_bumper_radius_label, self.property_bumper_radius, self.property_bumper_speed_label, self.property_bumper_speed, self.property_bumper_apply ]
		# RACCZ mode properties widgets
		self.property_raccz_number = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Numero bumper:", validatecommand=do_nothing, state='readonly' )
		self.property_raccz_center_label = tk.Label(master=self.frame_properties,text="Centro:")
		self.property_raccz_center_x = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="X:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_center_y = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Y:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_radius_label = tk.Label(master=self.frame_properties,text="Radio:")
		self.property_raccz_radius = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Radio:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_angle_label = tk.Label(master=self.frame_properties,text="Angulo:")
		self.property_raccz_angle = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Angulo:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_accel_label = tk.Label(master=self.frame_properties, text="Aceleracion:")
		self.property_raccz_accel = rceditor_custom_widgets.TextBoxWithDescription( master=self.frame_properties, description="Aceleracion:", validatecommand=RACCZ_RealNumber_Validation )
		self.property_raccz_invis_variable = tk.BooleanVar()
		self.property_raccz_invis = tk.Checkbutton(master=self.frame_properties, text="Invisible", var=self.property_raccz_invis_variable, command=self.RACCZ_Property_Checkbox_Click_Callback )
		self.property_raccz_apply = tk.Button( master = self.frame_properties, text="Forzar aplicar cambios", command = self.Apply_Selected_RACCZ_Changes)
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
				self.window_statusbar.set_field_1("%s", "Nuevo segmento: seleccione punto inicial")
				self.canvas_mapview.Set_Cursor_Cross()
			elif new_segment_submode == Segment_SubMode.edit:
				self.button_edit_segm.configure( bg = "green" )
				self.window_statusbar.set_field_1("%s", "Seleccione un segmento")
				self.canvas_mapview.Set_Cursor_Arrow()
			#elif new_segment_submode == Segment_SubMode.delete:
			#	self.button_del_segm.configure( bg = "green" )
			# Actions to do regardless of the new mode
			self.button_del_segm.config(state="disabled")		# Disable erase button (15/11/2020)
			self.current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start	# Restart "add new segment" sequence


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
				self.window_statusbar.set_field_1("%s", "Nuevo bumper: seleccione punto central")
			elif new_bumper_submode == Bumper_SubMode.edit:
				self.button_edit_bumper.configure( bg = "green" )
				self.window_statusbar.set_field_1("%s", "Seleccione un bumper")
			#elif new_bumper_submode == Bumper_SubMode.delete:
			#	self.button_del_bumper.configure( bg = "green" )


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
				current_raccz_submode = RACCZ_Add_Stages.St0_Choose_Center
				self.window_statusbar.set_field_1("%s", "Nueva zona acel circular: seleccione punto central")
			elif new_raccz_submode == RACCZ_SubMode.edit:
				self.button_edit_raccz.configure( bg = "green" )
			#elif new_raccz_submode == RACCZ_SubMode.delete:
			#	self.button_del_raccz.configure( bg = "green" )



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

		self.img_new_raccz_icon = ImageTk.PhotoImage(Image.open("icons/new_raccz-16.png"))
		self.img_edit_raccz_icon = ImageTk.PhotoImage(Image.open("icons/edit_raccz-16.png"))
		self.img_del_raccz_icon = ImageTk.PhotoImage(Image.open("icons/del_raccz-16.png"))

		self.img_new_bumper_icon = ImageTk.PhotoImage(Image.open("icons/new_bumper-16.png"))
		self.img_edit_bumper_icon = ImageTk.PhotoImage(Image.open("icons/edit_bumper-16.png"))
		self.img_del_bumper_icon = ImageTk.PhotoImage(Image.open("icons/del_bumper-16.png"))

		self.img_table_icon = ImageTk.PhotoImage(Image.open("icons/table-16.png"))



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
						self.window_statusbar.set_field_1("%s %d %s", "Segmento ", segment_found ," seleccionado" )
					else:
						logging.debug("No se ha encontrado ningun segmento.")
						self.UnSelect_Segment()
						self.canvas_mapview.UnHighlight_Segments()
						self.window_statusbar.set_field_1("%s", "Segmentos deseleccionados" )

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
						self.window_statusbar.set_field_1("%s", "Bumpers deseleccionados" )

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
						self.window_statusbar.set_field_1("%s %d %s", "Zona acel circ ", raccz_found ," seleccionada" )
					else:
						logging.debug("No se ha encontrado ninguna zona de aceleracion circular.")
						self.UnSelect_RACCZ()
						self.canvas_mapview.UnHighlight_RACCZ()
						self.window_statusbar.set_field_1("%s", "Zonas acel circ deseleccionadas" )

				if self.current_mode == Mode.segment and self.current_segment_submode == Segment_SubMode.add:
					if ( self.current_segment_add_stage == Segment_Add_Stages.St0_Choose_Start):
						logging.debug( "Seleccionado como punto inicial: x = " + str(map_x) + ", y = " + str(map_y) )
						self.temp_segment_data_to_create.start.x = map_x
						self.temp_segment_data_to_create.start.y = map_y
						self.window_statusbar.set_field_1("%s", "Nuevo segmento: seleccione punto final")
						self.current_segment_add_stage = Segment_Add_Stages.St1_Choose_End
					elif ( self.current_segment_add_stage == Segment_Add_Stages.St1_Choose_End):
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
							self.temp_segment_data_to_create.segm_type = rceditor_maps.Segment_Type.wall	# In case nothing is selected, set a default type
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
						self.window_statusbar.set_field_1("%s", "Nuevo segmento: seleccione punto inicial")
						self.current_segment_add_stage = Segment_Add_Stages.St0_Choose_Start
					else:
						logging.error( "Error de programacion: etapa actual de añadir segmento tiene un valor no valido " + str(self.current_segment_add_stage) )


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
			if messagebox.askokcancel("Cerrar programa", "¿Realmente desea cerrar el programa?"):
				self.window_main_editor.destroy()
		else:		# no map loaded
			self.window_main_editor.destroy()


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

			# Load map images
			self.canvas_mapview.Load_Images( self.mapa_cargado, self.preferences )
			logging.debug( "Representando mapa en editor... " )
			self.canvas_mapview.DrawAll( self.mapa_cargado )

			self.window_main_editor.title( "RoadCoin Level Editor - " + self.loaded_map_filename )
			self.map_loaded = True
			self.EnableMenuItems_MapLoaded()

			self.window_statusbar.set_field_1("%s %s %s", "Mapa ", open_map_filename ," cargado" )
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
		self.window_statusbar.set_field_1("%s", "Mapa cerrado" )


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
			self.window_statusbar.set_field_1("%s", "Aplicando zoom, espere por favor" )
			self.canvas_mapview.zoomlevel += zoom_increment
			self.canvas_mapview.DrawAll( self.mapa_cargado )
			self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
			logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (incrementado)" )
			self.window_statusbar.set_field_1("%s %f %s", "Zoom ", self.canvas_mapview.zoomlevel , "aplicado. Listo" )
		else:
			logging.debug("Ya estamos en el minimo zoom, no se cambia")
			self.window_statusbar.set_field_1("%s", "Zoom minimo alcanzado" )

	def SetZoomLevel(self, zoomlevel):
		self.window_statusbar.set_field_1("%s", "Aplicando zoom, espere por favor" )
		self.canvas_mapview.zoomlevel = zoomlevel
		self.canvas_mapview.DrawAll( self.mapa_cargado )
		self.window_statusbar.set_field_3("%s", "Zoom: " + str(int(self.canvas_mapview.zoomlevel*100)) + "%")
		logging.debug("Nivel de zoom = " + str(self.canvas_mapview.zoomlevel) + " (ajustado)" )
		self.window_statusbar.set_field_1("%s %f %s", "Zoom ", self.canvas_mapview.zoomlevel , "aplicado. Listo" )


	def Unselect_All( self ):
		self.UnSelect_Segment()
		self.UnSelect_Bumper()
		self.UnSelect_RACCZ()
		self.canvas_mapview.UnHighlight_All()



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
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title="Error", message="Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: " + str( sys.exc_info()[0] ) + "\n" + str(e) )
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
				answer = tk.messagebox.askyesnocancel("Eliminar segmento", "¿Desea eliminar el segmento numero " + selected_segment + "?")
				logging.debug( "Pregunta eliminar segmento, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeleteSegment( int(selected_segment) )
				self.mapa_cargado.Segments_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", "Segmento ", selected_segment , " borrado" )
			else:
				tk.messagebox.showerror(title="Error", message="El numero de segmento seleccionado (" + selected_segment + ") no es valido.")
				logging.dialog( "Error de programación: El numero de segmento seleccionado (" + selected_segment + ") no es valido." )
		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")


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
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title="Error", message="Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: " + str( sys.exc_info()[0] ) + "\n" + str(e) )
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
				answer = tk.messagebox.askyesnocancel("Eliminar bumper", "¿Desea eliminar el bumper numero " + selected_bumper + "?")
				logging.debug( "Pregunta eliminar bumper, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeletePinballBumper( int(selected_bumper) )
				self.mapa_cargado.Bumpers_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", "Bumper ", selected_bumper , " borrado" )
			else:
				tk.messagebox.showerror(title="Error", message="El numero de bumper seleccionado (" + selected_bumper + ") no es valido.")
				logging.dialog( "Error de programación: El numero de bumper seleccionado (" + selected_bumper + ") no es valido." )
		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")

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
			except Exception as e:
				logging.exception(e)
				tk.messagebox.showerror(title="Error", message="Valores no válidos, no se tienen en cuenta las modificaciones.\n\n\nExcepcion: " + str( sys.exc_info()[0] ) + "\n" + str(e) )
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
				answer = tk.messagebox.askyesnocancel("Eliminar zona acel circular", "¿Desea eliminar la zona de aceleracion circular numero " + selected_raccz + "?")
				logging.debug( "Pregunta eliminar zona de aceleracion circular, el usuario ha respondido answer = " + str(answer) )
				if (answer is None) or (answer == False) :
					return	# Do nothing
				# The selected segment will be deleted
				self.mapa_cargado.DeleteRACCZ( int(selected_raccz) )
				self.mapa_cargado.RACCZ_Reenumerate()
				self.canvas_mapview.DrawAll( self.mapa_cargado )
				self.Unselect_All()
				self.window_statusbar.set_field_1("%s %s %s", "Zona acel circ ", selected_raccz , " borrada" )
			else:
				tk.messagebox.showerror(title="Error", message="El numero de zona aceleracion circular seleccionado (" + selected_raccz + ") no es valido.")
				logging.dialog( "Error de programación: El numero de zona de aceleracion circular seleccionado (" + selected_raccz + ") no es valido." )
		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")


	def Toggle_Show_Hide_Table( self ):
		# PROVISIONAL, DEBE SER PROBADO (TODO)
		if self.map_loaded == True:
			if self.segment_table is None:		# Segment table is not open (the object does not exist)
				self.segment_table = rceditor_tables.Segment_Table_Window( master = self.window_main_editor, Map = self.mapa_cargado , owner=self )
			else:					# Segment table is already open
				del self.segment_table



	def Segment_Property_RealNumber_Change_FocusOut_Validation_Callback( self, widget_name, text_before_change, text_after_change ):
		# This is the validation function called everytime an entry widget loses focus (if everything is set up correctly, of course)
		logging.debug( "Llamada a función Segment_Property_RealNumber_Change_FocusOut_Validation_Callback: Modo = " + mode_names.get( self.current_mode ) + \
				", widget_name = " + str(widget_name) + ", text_before_change = " + text_before_change\
				+ ", text_after_change = " + text_after_change )
		if self.map_loaded == True:
			if self.current_mode == Mode.segment:
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_Selected_Segment_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title="Error", message="Valor no válido, no es un número. No se tienen en cuenta las modificaciones.")
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
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_Selected_Bumper_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title="Error", message="Valor no válido, no es un número. No se tienen en cuenta las modificaciones.")
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
				if isFloat(text_after_change) == True:
					logging.debug("El nuevo texto es un numero.")
					self.Apply_Selected_RACCZ_Changes()
					return(True)
				else:
					logging.debug("El nuevo texto no es un numero.")
					tk.messagebox.showerror(title="Error", message="Valor no válido, no es un número. No se tienen en cuenta las modificaciones.")
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
				tk.messagebox.showinfo(title="Comprobación mapa", message="No se han encontrado errores.")
			else:
				tk.messagebox.showerror(title="Comprobación mapa", message="Se han encontrado los siguientes errores. \n" + error_list )		
		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")

	def ReenumerateSegments( self ):
		# For DEBUG purposes	
		if self.map_loaded == True:
			self.mapa_cargado.Segments_Reenumerate()
			self.canvas_mapview.DrawAll( self.mapa_cargado )
		else:
			tk.messagebox.showerror(title="Error", message="No hay ningún mapa cargado.")
