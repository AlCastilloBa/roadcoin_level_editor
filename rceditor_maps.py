
from enum import Enum


class Segment_Type(Enum):
	wall = 0
	goal = 1
	death = 2
	pinball_flipper_L = 3
	pinball_flipper_R = 4

Segment_Type_Names = { 
	Segment_Type.wall               : "Ningun modo seleccionado" , 
	Segment_Type.goal               : "Modo general" , 
	Segment_Type.death              : "Modo imagenes" , 
	Segment_Type.pinball_flipper_L  : "Modo fondo giratorio" , 
	Segment_Type.pinball_flipper_R  : "Modo segmentos" , 
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
	Segment_list = None	# List of Class Segment
	Coin_Image_Path = None	# String
	Fixed_Background_Path = None	# String
	Coin_Does_Not_Rotate = None 	# Boolean
	Countdown = None	# Boolean
	CountDown_Time = None	# Int
	Rotating_Background = None	# Boolean
	Rotating_Background_Path = None		# String
	Rotating_Background_Left_X_Pos = None	# Int
	Rotating_Background_Up_Y_Pos = None	# Int
	Rotating_Background_Right_X_Pos = None	# Int
	Rotating_Background_Down_Y_Pos = None	# Int
	Rotating_Background_Center = None	# Class Point
	Wall_Segment_Image_Path = None		# String
	Goal_Segment_Image_Path = None		# String
	Death_Segment_Image_Path = None		# String
	Music_Path = None		# String
	pinball_bumpers_number = None		# Int
	pinball_bumpers_list = None	# List of Class Pinball Bumper
	flippers_angle = None		# Real
	round_accel_zones_number = None		# Int
	list_round_acel_zones = None		# List of Class Round_Acceleration_Zones
	Description_Image_path = None		# String

	def __init__(self):
		pass

	def LoadFile(self, filename):
		pass

	def SaveFile(self, filename):
		pass




