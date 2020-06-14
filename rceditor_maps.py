
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

	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

class Segment():
	start = None # Class Point
	end = None   # Class Point
	segm_type = None  # Class Segment Type
	invisible = None  # Boolean

	def __init__(self, start, end, segm_type, invisible):
		self.start = start
		self.end = end
		self.segm_type = segm_type
		self.invisible = invisible

class Pinball_Bumper():
	center = None # Class Point
	radius = None  # Real
	exit_speed = None # Real
	
	def __init__(self, center, radius, exit_speed):
		self.center = center
		self.radius = radius
		self.exit_speed = exit_speed

class Round_Acceleration_Zone():
	center = None # Class Point
	radius = None # Real
	angle = None # Real
	acceleration = None #  Real
	invisible = None # Boolean

	def __init__(self, center, radius, angle, acceleration, invisible ):
		self.center = center
		self.radius = radius
		self.angle = angle
		self.acceleration = acceleration
		self.invisible = invisible

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
				rotating_background_left_x_pos = int(  line.split("((",1)[1].split(",",1)[0] )  
				rotating_background_up_y_pos = int(  line.split(",",1)[1].split("),(",1)[0]  ) 
				rotating_background_right_x_pos = int(  line.split("),(",1)[1].split(",",1)[0]  )
				rotating_background_down_y_pos = int(  line.split(",",5)[3].strip(")") ) 
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




