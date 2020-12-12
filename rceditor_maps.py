
from enum import Enum
import logging
import sys


class Segment_Type(Enum):
	wall = 0
	goal = 1
	death = 2
	pinball_flipper_L = 3
	pinball_flipper_R = 4

Segment_Type_Names = { 
	Segment_Type.wall               : "Pared" , 
	Segment_Type.goal               : "Meta" , 
	Segment_Type.death              : "Muerte" , 
	Segment_Type.pinball_flipper_L  : "Pinball Flipper L" , 
	Segment_Type.pinball_flipper_R  : "Pinball Flipper R" , 
}


class Rotation_Type(Enum):
	camera = 0
	fixed_point = 1
	coin = 2
	origin = 3
	no_rot = 4

Rotation_Type_Names = {
	Rotation_Type.camera        : "Camara", 
	Rotation_Type.fixed_point   : "Punto fijo", 
	Rotation_Type.coin          : "Moneda", 
	Rotation_Type.origin        : "Origen", 
	Rotation_Type.no_rot        : "Sin giro"
}

class Point():
	x = None
	y = None

#	def __init__(self, x=0, y=0):
	def __init__(self, x=None, y=None, copy_ref=None):
		if ( x is not None ) and ( y is not None ) and ( copy_ref is None):
			self.x = x
			self.y = y
		elif ( x is None ) and ( y is None ) and ( copy_ref is not None):
			# Pseudo copy constructor
			self.x = copy_ref.x
			self.y = copy_ref.y
		elif ( x is None ) and ( y is None ) and ( copy_ref is None):
			self.x = None
			self.y = None	
		else:
			raise ValueError("Al crear objeto clase Point, argumentos no validos: se debe especificar el conjunto completo de argumentos (x, y) o bien copy_ref, o bien ninguno.")

	def copy( self, copy_ref ):
		# Replace coordinates with another point's coordinates
		self.x = copy_ref.x
		self.y = copy_ref.y		



class Segment():
	start = None # Class Point
	end = None   # Class Point
	segm_type = None  # Class Segment Type
	invisible = None  # Boolean

	def __init__(self, start=None, end=None, segm_type=None, invisible=None, copy_ref=None):
		if (start is not None) and (end is not None) and (segm_type is not None) and (invisible is not None) and (copy_ref is None):
			self.start = start
			self.end = end
			self.segm_type = segm_type
			self.invisible = invisible
		elif (start is None) and (end is None) and (segm_type is None) and (invisible is None) and (copy_ref is not None):
			# Pseudo copy constructor
			self.start = Point( copy_ref.start.x , copy_ref.start.y )
			self.end = Point( copy_ref.end.x , copy_ref.end.y )
			self.segm_type = copy_ref.segm_type
			self.invisible = copy_ref.invisible
		else:
			raise ValueError("Al crear objeto clase Segment, argumentos no validos: se debe especificar el conjunto completo de argumentos (start,end,segm_type,invisible) o bien copy_ref.")			

class Pinball_Bumper():
	center = None # Class Point
	radius = None  # Real
	exit_speed = None # Real
	
	def __init__(self, center=None, radius=None, exit_speed=None, copy_ref=None):
		if (center is not None) and (radius is not None) and (exit_speed is not None) and (copy_ref is None):
			self.center = center
			self.radius = radius
			self.exit_speed = exit_speed
		elif (center is None) and (radius is None) and (exit_speed is None) and (copy_ref is not None):
			# Pseudo copy constructor
			self.center = Point( copy_ref.center.x, copy_ref.center.y )
			self.radius = copy_ref.radius
			self.exit_speed = copy_ref.exit_speed
		else:
			raise ValueError("Al crear objeto clase Pinball_Bumper, argumentos no validos: se debe especificar el conjunto completo de argumentos (center,radius,exit_speed) o bien copy_ref.")

class Round_Acceleration_Zone():
	center = None # Class Point
	radius = None # Real
	angle = None # Real
	acceleration = None #  Real
	invisible = None # Boolean

	def __init__(self, center=None, radius=None, angle=None, acceleration=None, invisible=None, copy_ref=None ):
		if (center is not None) and (radius is not None) and (angle is not None) and (acceleration is not None) and (invisible is not None) and (copy_ref is None):
			self.center = center
			self.radius = radius
			self.angle = angle
			self.acceleration = acceleration
			self.invisible = invisible
		elif (center is None) and (radius is None) and (angle is None) and (acceleration is None) and (invisible is None) and (copy_ref is not None):
			# Pseudo copy constructor
			self.center = Point( copy_ref.center.x, copy_ref.center.y )
			self.radius = copy_ref.radius
			self.angle = copy_ref.angle
			self.acceleration = copy_ref.acceleration
			self.invisible = copy_ref.invisible
		else:
			raise ValueError("Al crear objeto clase Round_Acceleration_Zone, argumentos no validos: se debe especificar el conjunto completo de argumentos (center,radius,angle,acceleration,invisible) o bien copy_ref.")


class Map():
	map_name = None		# String
	map_description = None	# String
	segment_number = None	# Int
	rotation_type = None	# Class Rotation_Type
	rotation_center = None  # Class Point
	max_angle = None        # Real
	coin_starting_point = None # Class Point
	gravity = None		# Real
	# segment_list = None	# List of Class Segment
	segment_dict = dict()	# Dictionary of Class Segment
	coin_image_path = None	# String
	fixed_background_path = None	# String
	coin_does_not_rotate = None 	# Boolean
	countdown = None	# Boolean
	countdown_time = None	# Int
	rotating_background = None	# Boolean
	rotating_background_path = None		# String
	rotating_background_left_x_pos = None	# Int
	rotating_background_up_y_pos = None	# Int
	rotating_background_right_x_pos = None	# Int
	rotating_background_down_y_pos = None	# Int
	rotating_background_center = None	# Class Point
	wall_segment_image_path = None		# String
	goal_segment_image_path = None		# String
	death_segment_image_path = None		# String
	music_path = None		# String
	pinball_bumpers_number = None		# Int
	# pinball_bumpers_list = None	# List of Class Pinball Bumper
	pinball_bumpers_dict = dict()	# Dictionary of Class Pinball Bumper
	flippers_angle = None		# Real
	round_accel_zones_number = None		# Int
	# list_round_acel_zones = None		# List of Class Round_Acceleration_Zones
	dict_round_acel_zones = dict()		# Dictionary of Class Round_Acceleration_Zones
	Description_Image_path = None		# String
	scale = None		# Int

	def __init__(self):
		pass

	def __del__(self):
		logging.debug( "Destruyendo objeto clase Map" )
		self.segment_dict.clear()
		self.pinball_bumpers_dict.clear()
		self.dict_round_acel_zones.clear()

	def LoadFile(self, filename):
		file1 = open( filename , 'r' )
		Lines = file1.readlines()
		for idx, line in enumerate(Lines):
			# Strip newline and spaces
			line = line.strip()
			logging.debug( "Leida linea "+ str(idx) + ": " + line )
			# Find and strip remarks at the right side of " #"
			if line.find(" #") != -1:
				line = line.split(" #",1)[0]
			# Check if line is empty
			if line == "":
				logging.debug( "Linea vacia")
			# Check if first character is "#" --> This is a remark
			elif line[0] == '#':
				logging.debug( "This is a comment, nothing has to be done")
			elif len(line) == 0:
				logging.debug( "Empty line.")
			elif line.find("nombre") != -1:
				self.map_name = line.split("=",1)[1].strip()
				logging.debug( "Encontrado nombre mapa = " + self.map_name )
			elif line.find("descripcion") != -1:
				self.map_description = line.split("=",1)[1].strip()
				logging.debug( "Encontrado nombre mapa = " + self.map_description )
			elif line.find("num_segmentos") != -1:
				if self.segment_number is not None:
					# Possible two declarations of segment number
					logging.debug( "Posiblemente dos declaraciones de num_segmentos" )
					sys.exit("Possibly two declarations of segment number" )
				else:
					self.segment_number = int( line.split("=",1)[1].strip() )
					logging.debug( "Encontrado num_segmentos = " + str(self.segment_number) )
			elif line.find("modo_giro_mapa") != -1:
				self.rotation_type = int( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado modo_giro_mapa = " + Rotation_Type_Names.get( Rotation_Type(self.rotation_type) ) )
			elif line.find("punto_giro") != -1:
				# Cadena a descomponer punto_giro=(x,y)
				self.rotation_center = Point()
				self.rotation_center.x = float( line.split("=",1)[1].strip().split(",",1)[0].replace("(","")  )
				self.rotation_center.y = float( line.split("=",1)[1].strip().split(",",1)[1].replace(")","")  )		
				logging.debug( "Encontrado punto_giro --> x = " + str(self.rotation_center.x) +  ", y = " + str(self.rotation_center.y) )
			elif line.find("angulo_max") != -1:
				self.max_angle = line.split("=",1)[1].strip()
				logging.debug( "Encontrado angulo_max = " + str(self.max_angle) )
			elif line.find("pos_inicial_moneda") != -1:
				# Cadena a descomponer pos_inicial_moneda=(%lf,%lf)
				self.coin_starting_point = Point()
				self.coin_starting_point.x = float( line.split("=",1)[1].strip().split(",",1)[0].replace("(","")  )
				self.coin_starting_point.y = float( line.split("=",1)[1].strip().split(",",1)[1].replace(")","")  )		 
				logging.debug( "Encontrado pos_inicial_moneda --> x = " + str(self.coin_starting_point.x) +  ", y = " + str(self.coin_starting_point.y) )
			elif line.find("gravedad") != -1:
				self.gravity = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado gravedad = " + str(self.gravity) )
			elif line.find("imagen_moneda") != -1:
				self.coin_image_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_moneda = " + self.coin_image_path )
			elif line.find("imagen_fondo") != -1:
				self.fixed_background_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_fondo = " + self.fixed_background_path )
			elif line.replace(" ","").find("segmento[") != -1:
				# Cadena a descomponer segmento[%d]=((%lf,%lf),(%lf,%lf),%d, %d)
				segm_aux = Segment( start=Point( float(line.split("((",1)[1].split(",",1)[0]) , float(line.split(",",1)[1].split("),(",1)[0]) ) , \
							end=Point( float(line.split("),(",1)[1].split(",",1)[0]) , float(line.split(",",5)[3].strip(")") ) )  , \
							segm_type = int(line.split("),",5)[2].split(",",1)[0])  , \
							invisible = bool( int( line.split(",",6)[5].split(")",1)[0] )  ) )
				indice_aux = int(line.split('[', 1)[1].split(']')[0].replace("(","") )  
				self.segment_dict.setdefault( indice_aux, segm_aux )
				logging.debug( "Encontrado segmento, num " + str(indice_aux) + \
						", start --> x = " + str(self.segment_dict.get(indice_aux).start.x) + \
						", y = " + str(self.segment_dict.get(indice_aux).start.y) + \
						"; end --> x = " + str(self.segment_dict.get(indice_aux).end.x) + \
						", y = " + str(self.segment_dict.get(indice_aux).end.y) + \
						"; tipo = " + Segment_Type_Names.get( Segment_Type(self.segment_dict.get(indice_aux).segm_type ) ) + \
						", invisible = " + str(self.segment_dict.get(indice_aux).invisible ) \
						)
			elif line.find("fondo_giratorio") != -1:
				self.rotating_background = bool( int( line.split("=",1)[1].strip() ) )
				logging.debug( "Encontrado fondo_giratorio = " + str( self.rotating_background ) )
			elif line.find("imagen_fnd_giratorio") != -1:
				self.rotating_background_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_fnd_giratorio = " + self.rotating_background_path )
			elif line.find("pos_fnd_giratorio") != -1:
				# Cadena a descomponer pos_fnd_giratorio=((%d,%d),(%d,%d))
				self.rotating_background_left_x_pos = int(  line.split("((",1)[1].split(",",1)[0] )  
				self.rotating_background_up_y_pos = int(  line.split(",",1)[1].split("),(",1)[0]  ) 
				self.rotating_background_right_x_pos = int(  line.split("),(",1)[1].split(",",1)[0]  )
				self.rotating_background_down_y_pos = int(  line.split(",",5)[3].strip(")") ) 
				logging.debug( "Encontrado pos_fnd_giratorio, izq = " + str( self.rotating_background_left_x_pos ) + ", arr = " + str( self.rotating_background_up_y_pos ) + \
					", der = " + str( self.rotating_background_right_x_pos) + ", aba = " + str( self.rotating_background_down_y_pos ) )
			elif line.find("centro_giro_fnd_gir") != -1:
				self.rotating_background_center = Point()
				self.rotating_background_center.x = float( line.split("=",1)[1].strip().split(",",1)[0].replace("(","")  )
				self.rotating_background_center.y = float( line.split("=",1)[1].strip().split(",",1)[1].replace(")","")  )	
				logging.debug( "Encontrado centro_giro_fnd_gir --> x = " + str(self.rotating_background_center.x) +  ", y = " + str(self.rotating_background_center.y) )
			elif line.find("escala") != -1:
				self.scale = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado escala = " + str(self.scale) )
			elif line.find("ruta_musica") != -1:
				self.music_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado ruta_musica = " + self.music_path )
			elif line.find("num_bumpers") != -1:
				if self.pinball_bumpers_number is not None:
					# Possible two declarations of pinball bumpers number
					logging.debug( "Posiblemente dos declaraciones de num_bumpers" )
					sys.exit("Possibly two declarations of bumpers number" )
				else:
					self.pinball_bumpers_number = int( line.split("=",1)[1].strip() )
					logging.debug( "Encontrado num_bumpers = " + str(self.pinball_bumpers_number) )
			elif line.replace(" ","").find("bumper[") != -1: 
				# Cadena a descomponer bumper[%d]=((%lf,%lf),%f,%f)
				bumper_aux = Pinball_Bumper( center=Point( float(line.split("((",1)[1].split(",",1)[0]) , float(line.split(",",1)[1].split("),",1)[0]) ) , \
							radius=float(  line.split("),",1)[1].split(",",1)[0] )  , \
							exit_speed=float( line.split(",",3)[3].split(")",1)[0] )   \
							)
				indice_aux = int(line.split('[', 1)[1].split(']')[0].replace("(","") )
				self.pinball_bumpers_dict.setdefault( indice_aux, bumper_aux )
				logging.debug( "Encontrado bumper num " + str(indice_aux) + \
						" --> x = " + str(self.pinball_bumpers_dict.get(indice_aux).center.x) + \
						", y = " + str(self.pinball_bumpers_dict.get(indice_aux).center.y) + \
						", radius = " + str(self.pinball_bumpers_dict.get(indice_aux).radius ) + \
						", exit_speed = " + str(self.pinball_bumpers_dict.get(indice_aux).exit_speed ) \
						)
			elif line.find("angulo_flippers") != -1:
				self.flippers_angle = float( line.split("=",1)[1].strip() )
				logging.debug( "Encontrado nombre mapa = " + str(self.flippers_angle) )
			elif line.find("tiempo_cuenta_atras") != -1: 
				self.countdown_time = int( line.split("=",1)[1].strip() )
				self.countdown = True
				logging.debug( "Encontrado nombre mapa = " + str(self.countdown_time) )
			elif line.find("num_zonas_acel_circ") != -1:
				if self.round_accel_zones_number is not None:
					# Possible two declarations of round accel zones number
					logging.debug( "Posiblemente dos declaraciones de num_zonas_acel_circ" )
					sys.exit("Possibly two declarations of round accel zones number" )
				else:
					self.round_accel_zones_number = int(  line.split("=",1)[1].strip()  )
					logging.debug( "Encontrado num_zonas_acel_circ = " + str(self.round_accel_zones_number) )
			elif line.find("zona_acel_circ") != -1:
				# Cadena a descomponer zona_acel_circ[%d]=((%lf,%lf),%f,%f,%f,%d)
				racc_aux = Round_Acceleration_Zone( center=Point( float(line.split("((",1)[1].split(",",1)[0]) , float(line.split(",",1)[1].split("),",1)[0]) )  , \
								radius= float(  line.split("),",1)[1].split(",",1)[0] )  , \
								angle= float(line.split(",",5)[3].split(",",1)[0])  , \
								acceleration=  float(line.split(",",5)[4].split(",",1)[0]) , \
								invisible=  bool( int( line.split(",",6)[5].split(")",1)[0] )  ) \
								)
				indice_aux = int(line.split('[', 1)[1].split(']')[0].replace("(","") )
				self.dict_round_acel_zones.setdefault( indice_aux, racc_aux )
				logging.debug( "Encontrado zona acel circ, num " + str(indice_aux) + \
						" --> x = " + str(self.dict_round_acel_zones.get(indice_aux).center.x) + \
						", y = " + str(self.dict_round_acel_zones.get(indice_aux).center.y) + \
						", angle = " + str(self.dict_round_acel_zones.get(indice_aux).angle ) + \
						", acceleration = " + str(self.dict_round_acel_zones.get(indice_aux).acceleration ) + \
						", invisible = " + str(self.dict_round_acel_zones.get(indice_aux).invisible ) \
						)
			elif line.find("no_rot_moneda") != -1:
				self.coin_does_not_rotate = True
				logging.debug( "Encontrado no_rot_moneda" )
			elif line.find("imagen_segm_pared") != -1:
				self.wall_segment_image_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_segm_pared = " + self.wall_segment_image_path ) 
			elif line.find("imagen_segm_meta") != -1:
				self.goal_segment_image_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_segm_meta = " + self.goal_segment_image_path )
			elif line.find("imagen_segm_muerte") != -1:
				self.death_segment_image_path = line.split("=",1)[1].strip()
				logging.debug( "Encontrado imagen_segm_muerte = " + self.death_segment_image_path )
			####################################################
			# Add new options at this point
			####################################################
			else:
				logging.debug( "Expresion no reconocida, se ignora" )	

		file1.close()

	def SaveFile(self, filename):
		pass


	def CheckMapErrorList( self ):
		# This function makes some verifications in order to check if map data is valid
		# It returns a tuple containing:
		#  - map_data_ok = True/False
		#  - error_list. String containing the error list. If no errors found, then the string will be empty
		
		map_data_ok = True
		error_list = ""
		# Checking if data is defined
		if (self.map_name is None) or (self.map_name==""):			# String
			map_data_ok = False
			error_list = error_list + "Nombre del mapa no definido.\n"
		if (self.map_description is None) or (self.map_description==""):	# String
			map_data_ok = False
			error_list = error_list + "Descripción del mapa no definida.\n"
		if (self.segment_number is None) or (self.segment_number==0):		# Int
			map_data_ok = False
			error_list = error_list + "Numero de segmentos no definido.\n"
		if (self.rotation_type is None ) or ( self.rotation_type not in [item.value for item in Rotation_Type] ):	# Class Rotation_Type
			map_data_ok = False
			error_list = error_list + "Tipo rotacion no definida.\n"
		else:
			if (self.rotation_type == Rotation_Type.fixed_point):
				if (self.rotation_center is None ):  # Class Point
					map_data_ok = False
					error_list = error_list + "Centro de giro no definido (y rotacion alrededor de punto fijo).\n"
				elif (self.rotation_center.x is None) or (self.rotation_center.y is None):
					map_data_ok = False
					error_list = error_list + "Alguna componente del centro de giro no definido.\n"
		if (self.max_angle is None ):        # Real
			map_data_ok = False
			error_list = error_list + "Angulo máximo no definido.\n"
		if (self.coin_starting_point is None ):			  # Class Point
			map_data_ok = False
			error_list = error_list + "Punto de inicio de la moneda no definido.\n"
		elif (self.coin_starting_point.x is None ) or (self.coin_starting_point.y is None ):
			map_data_ok = False
			error_list = error_list + "Alguna componente del punto de inicio de la moneda no definido.\n"
		if (self.gravity is None ) or (self.gravity == 0 ) :		# Real
			map_data_ok = False
			error_list = error_list + "La gravedad no está definida.\n"
		if ( self.coin_image_path is None ) or ( self.coin_image_path=="" ):	# String
			map_data_ok = False
			error_list = error_list + "La imagen de la moneda no está definida.\n"
		if (self.fixed_background_path is None ) or (self.fixed_background_path=="" ):	# String
			map_data_ok = False
			error_list = error_list + "La imagen del fondo fijo no está definida.\n"
		#Note: coin_does_not_rotate = None is possible 	# Boolean
		if ( self.countdown is not None ): # Boolean
			if ( self.countdown == True ) and ( (self.countdown_time is None) or (self.countdown_time==0) ):	  	# Int
				map_data_ok = False
				error_list = error_list + "Se espera tiempo cuenta atras, pero no está definido.\n"

		if ( self.rotating_background is not None ): 	# Boolean
			if (self.rotating_background==True) and (( self.rotating_background_path is None ) or ( self.rotating_background_path=="" ) ):  # String
				map_data_ok = False
				error_list = error_list + "Se espera imagen fondo giratorio, pero no está definido.\n"
			if (self.rotating_background==True) and ( (self.rotating_background_left_x_pos is None) or ( self.rotating_background_up_y_pos is None) or \
				(self.rotating_background_right_x_pos is None) or (self.rotating_background_down_y_pos is None) ):	# Int
				map_data_ok = False
				error_list = error_list + "Se espera imagen fondo giratorio, pero falta definir alguna posición del fondo.\n"
			if (self.rotating_background==True): 
				if ( self.rotating_background_center is None ):    # Class Point
					map_data_ok = False
					error_list = error_list + "Se espera imagen fondo giratorio, pero el centro de giro no está definido.\n"
				elif ( self.rotating_background_center.x is None ) or ( self.rotating_background_center.y is None ):
					map_data_ok = False
					error_list = error_list + "Se espera imagen fondo giratorio, pero alguna componente del centro de giro no está definido.\n"

		# Note: wall_segment_image_path = None	is possible	# String
		# Note: goal_segment_image_path = None	is possible	# String
		# Note: death_segment_image_path = None is possible		# String
		# Note: music_path = None is possible		# String

		if (self.pinball_bumpers_number is None) or (self.pinball_bumpers_number==0):		# Int
			map_data_ok = False
			error_list = error_list + "Numero de bumpers no definido.\n"
		if (self.round_accel_zones_number is None) or (self.round_accel_zones_number==0):		# Int
			map_data_ok = False
			error_list = error_list + "Numero de zonas de aceleración circular no definido.\n"

		#Note: flippers_angle = None	is possible	# Real
		#Note: Description_Image_path = None	is posible	# String
		#Note: scale = None is possible		# Int

		# Check data inside dictionaries. Check for invalid data

		for current_segm_index, current_segment in self.segment_dict.items():
			if ( current_segm_index > self.segment_number ) or ( current_segm_index < 0 ):
				map_data_ok = False
				error_list = error_list + "Indice de segmento " + current_segm_index + " parece incorrecto.\n"	
			if ( current_segment.start is None ):	# Class Point
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", no definido punto start.\n"
			elif ( current_segment.start.x is None ) or ( current_segment.start.y is None ):
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", alguna coordenada de punto start no está definida.\n"			
			if ( current_segment.end is None ):	# Class Point
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", no definido punto end.\n"
			elif ( current_segment.end.x is None ) or ( current_segment.end.y is None ):
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", alguna coordenada de punto end no está definida.\n"	
			if ( current_segment.segm_type is None ) or ( current_segment.segm_type not in [item.value for item in Segment_Type] ):	# Class Segment Type
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", tipo de segmento no definido.\n"
			if ( current_segment.invisible is None ): # Boolean
				map_data_ok = False
				error_list = error_list + "Segmento " + current_segm_index + ", visibilidad no definida.\n"

		for current_bumper_index, current_bumper in self.pinball_bumpers_dict.items():
			if ( current_bumper_index > self.pinball_bumpers_number ) or ( current_bumper_index < 0 ):
				map_data_ok = False
				error_list = error_list + "Indice de bumper " + current_bumper_index + " parece incorrecto.\n"	
			if ( current_bumper.center is None):	# Class Point
				map_data_ok = False
				error_list = error_list + "Bumper " + current_bumper_index + ", no definido punto centro.\n"
			elif ( current_bumper.center.x is None ) or ( current_bumper.center.y is None ):
				map_data_ok = False
				error_list = error_list + "Bumper " + current_bumper_index + ", alguna coordenada de punto centro no está definida.\n"	
			if ( current_bumper.radius is None ) or ( current_bumper.radius < 0 ): 		# Real
				map_data_ok = False
				error_list = error_list + "Bumper " + current_bumper_index + ", radio no definido o valor incorrecto.\n"		
			if ( current_bumper.exit_speed is None ) or ( current_bumper.exit_speed < 0 ): 		# Real
				map_data_ok = False
				error_list = error_list + "Bumper " + current_bumper_index + ", valocidad de salida no definida o valor incorrecto.\n"	

		for current_raccz_index, current_raccz in self.dict_round_acel_zones.items():
			if ( current_raccz_index > self.round_accel_zones_number ) or ( current_raccz_index < 0 ):
				map_data_ok = False
				error_list = error_list + "Indice de zona aceleracion circular " + current_raccz_index + " parece incorrecto.\n"
			if ( current_raccz.center is None):	# Class Point
				map_data_ok = False
				error_list = error_list + "Zona de aceleración circular " + current_raccz_index + ", no definido punto centro.\n"
			elif ( current_raccz.center.x is None ) or ( current_raccz.center.y is None ):
				map_data_ok = False
				error_list = error_list + "Zona de aceleración circular " + current_raccz_index + ", alguna coordenada de punto centro no está definida.\n"			
			if ( current_raccz.radius is None ) or ( current_raccz.radius < 0 ): 		# Real
				map_data_ok = False
				error_list = error_list + "Zona de aceleración circular " + current_raccz_index + ", radio no definido o valor incorrecto.\n"		
			if ( current_raccz.acceleration is None ) or ( current_raccz.acceleration < 0 ): 		# Real
				map_data_ok = False
				error_list = error_list + "Zona de aceleración circular " + current_raccz_index + ", aceleracion no definida o valor incorrecto.\n"
			if ( current_raccz.invisible is None ): # Boolean
				map_data_ok = False
				error_list = error_list + "Zona de aceleración circular " + current_raccz_index + ", visibilidad no definida.\n"

		# Check for unused numbers in dictionaries.
		if (self.segment_number is not None):
			if (self.segment_number != 0):
				unused_segment_numbers = [ x for x in range(0, self.segment_number-1 ) if x not in self.segment_dict.keys() ]
				if unused_segment_numbers:		# If the list is not empty	
					map_data_ok = False
					error_list = error_list + "Los siguientes numeros de segmentos no están definidos: " + str( unused_segment_numbers )
		if (self.pinball_bumpers_number is not None):
			if (self.pinball_bumpers_number != 0 ):
				unused_bumper_numbers = [ x for x in range(0, self.pinball_bumpers_number-1 ) if x not in self.pinball_bumpers_dict.keys() ]
				if unused_bumper_numbers:		# If the list is not empty
					map_data_ok = False
					error_list = error_list + "Los siguientes numeros de bumpers no están definidos: " + str( unused_bumper_numbers )
		if (self.round_accel_zones_number is not None):
			if (self.round_accel_zones_number != 0):
				unused_raccz_numbers = [ x for x in range(0, self.round_accel_zones_number-1 ) if x not in self.dict_round_acel_zones.keys() ]
				if unused_raccz_numbers:		# If the list is not empty
					map_data_ok = False
					error_list = error_list + "Los siguientes numeros de zonas de aceleracion circular no están definidos: " + str( unused_raccz_numbers )

		return map_data_ok, error_list


	def AddSegment( self, segm_ref ):
		logging.debug( "Añadiendo nuevo segmento (en la ultima posicion). ")
		# If the segment number is still not ititialized, we set it to zero
		if self.segment_number is None:
			self.segment_number = 0
		if segm_ref is not None:
			# Create new segment copying all properties from the segm_ref (pseudo copy constructor)
			segm_aux = Segment( copy_ref = segm_ref )
			# Add it to the dictionary
			self.segment_dict.setdefault( self.segment_number , segm_aux )
			self.segment_number = self.segment_number + 1
		else:
			logging.error( "Error de programacion: La referencia del segmento es None." )


	def DeleteSegment( self, segment_number_to_delete ):
		logging.debug( "Eliminando segmento " + str( segment_number_to_delete ) )
		self.segment_dict.pop( segment_number_to_delete )

	def Segments_Reenumerate( self ):
		logging.debug( "Compactando diccionario de segmentos" )
		dict_item_list = list( self.segment_dict.items() )
		# Sort according to the index (key)
		dict_item_list.sort(key=lambda segm_tuple: segm_tuple[0])
		# Empty the dictionary
		self.segment_dict.clear()
		# Reenumerate into the dictionary
		counter = 0
		for segment_tuples in dict_item_list:
			self.segment_dict.setdefault( counter, segment_tuples[1] )
			counter = counter + 1
		logging.debug( "Se han encontrado " + str(counter) + " segmentos." )
		self.segment_number = counter
		

	def  AddPinballBumper( self, bumper_ref ):
		logging.debug( "Añadiendo nuevo segmento (en la ultima posicion). ")
		# If the bumpers number is still not ititialized, we set it to zero
		if self.pinball_bumpers_number is None:
			self.pinball_bumpers_number = 0
		if bumper_ref is not None:
			# Create new bumper copying all properties from the bumper_ref (pseudo copy constructor)
			bumper_aux = Pinball_Bumper( copy_ref = bumper_ref )
			# Add it to the dictionary
			self.pinball_bumpers_dict.setdefault( self.pinball_bumpers_number , bumper_aux )
			self.pinball_bumpers_number = self.pinball_bumpers_number + 1
		else:
			logging.error( "Error de programacion: La referencia del bumper es None." )


	def DeletePinballBumper( self, bumper_number_to_delete ):
		logging.debug( "Eliminando pinball bumper " + str( bumper_number_to_delete ) )
		self.pinball_bumpers_dict.pop( bumper_number_to_delete )

	def Bumpers_Reenumerate( self ):
		logging.debug( "Compactando diccionario de bumpers" )
		dict_item_list = list( self.pinball_bumpers_dict.items() )
		# Sort according to the index (key)
		dict_item_list.sort(key=lambda bumper_tuple: bumper_tuple[0])
		# Empty the dictionary
		self.pinball_bumpers_dict.clear()
		# Reenumerate into the dictionary
		counter = 0
		for bumper_tuples in dict_item_list:
			self.pinball_bumpers_dict.setdefault( counter, bumper_tuples[1] )
			counter = counter + 1
		logging.debug( "Se han encontrado " + str(counter) + " bumpers." )
		self.pinball_bumpers_number = counter

	
	def AddRACCZ( self, raccz_ref ):
		logging.debug( "Añadiendo nueva zona de aceleración circular (en la ultima posicion). ")
		# If the raccz number is still not ititialized, we set it to zero
		if self.round_accel_zones_number is None:
			self.round_accel_zones_number = 0
		if raccz_ref is not None:
			# Create new raccz copying all properties from the raccz_ref (pseudo copy constructor)
			raccz_aux = Round_Acceleration_Zone( copy_ref = raccz_ref )
			# Add it to the dictionary
			self.dict_round_acel_zones.setdefault( self.round_accel_zones_number , raccz_aux )
			self.round_accel_zones_number = self.round_accel_zones_number + 1
		else:
			logging.error( "Error de programacion: La referencia del raccz es None." )


	def DeleteRACCZ( self, raccz_number_to_delete ):
		logging.debug( "Eliminando zona aceleracion circular " + str( raccz_number_to_delete ) )
		self.dict_round_acel_zones.pop( raccz_number_to_delete )


	def RACCZ_Reenumerate( self ):
		logging.debug( "Compactando diccionario de zonas de aceleracion circulares" )
		dict_item_list = list( self.dict_round_acel_zones.items() )
		# Sort according to the index (key)
		dict_item_list.sort(key=lambda raccz_tuple: raccz_tuple[0])
		# Empty the dictionary
		self.dict_round_acel_zones.clear()
		# Reenumerate into the dictionary
		counter = 0
		for raccz_tuples in dict_item_list:
			self.dict_round_acel_zones.setdefault( counter, raccz_tuples[1] )
			counter = counter + 1
		logging.debug( "Se han encontrado " + str(counter) + " zonas de aceleracion circulares." )
		self.round_accel_zones_number = counter


	def FindNearestSegmentPoint( self, point, threshold=None ):
		Nearest_Point_So_Far = Point( copy_ref=point )
		Min_Square_Distance_So_Far = 9999999999		# Infinity
		snap = False
		if threshold is None:
			threshold = 999999999		# Infinity
		else:
			threshold = threshold**2
		for current_segm_index, current_segment in self.segment_dict.items():
			dist_square = (  point.x - current_segment.start.x )**2 + (  point.y - current_segment.start.y )**2
			if ( dist_square < threshold ):
				if ( dist_square < Min_Square_Distance_So_Far ):
					Nearest_Point_So_Far.copy(  current_segment.start )
					Min_Square_Distance_So_Far = dist_square
					snap = True
			dist_square = (  point.x - current_segment.end.x )**2 + (  point.y - current_segment.end.y )**2
			if ( dist_square < threshold ):
				if ( dist_square < Min_Square_Distance_So_Far ):
					Nearest_Point_So_Far.copy(  current_segment.end )
					Min_Square_Distance_So_Far = dist_square
					snap = True
				
		# return Nearest_Point_So_Far
		return Nearest_Point_So_Far.x, Nearest_Point_So_Far.y, snap





