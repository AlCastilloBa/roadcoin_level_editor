import tkinter as tk
from tkinter import ttk		# Textbox
from tkinter import filedialog
import os


def do_nothing():
	x = 0

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

class StatusBar_MultiFields(tk.Frame):

	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.columnconfigure( 0, weight=1, minsize=500)
		self.columnconfigure( 1, weight=0, minsize=100)
		self.columnconfigure( 2, weight=0, minsize=100)
		self.label_field_1 = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label_field_2 = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label_field_3 = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label_field_1.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.label_field_2.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )
		self.label_field_3.grid(row=0, column=2,  padx=2, pady=2, sticky="nsew" )

	def set_field_1(self, format, *args):
		self.label_field_1.config(text=format % args)
		self.label_field_1.update_idletasks()

	def set_field_2(self, format, *args):
		self.label_field_2.config(text=format % args)
		self.label_field_2.update_idletasks()

	def set_field_3(self, format, *args):
		self.label_field_3.config(text=format % args)
		self.label_field_3.update_idletasks()

	def clear_field_1(self):
		self.label_field_1.config(text="")
		self.label_field_1.update_idletasks()

	def clear_field_2(self):
		self.label_field_2.config(text="")
		self.label_field_2.update_idletasks()

	def clear_field_3(self):
		self.label_field_3.config(text="")
		self.label_field_3.update_idletasks()

##############################################################################

class TextBoxWithDescription(tk.Frame):

	def __init__(self, master, description="Descripcion", validatecommand=do_nothing, state='normal'):
		tk.Frame.__init__(self, master )
		self.columnconfigure( 0 , weight=0, minsize=50)
		self.columnconfigure( 1 , weight=1, minsize=50)
		self.label_description = tk.Label(master=self,  text=description)
		self.entry_value = ttk.Entry(master=self, validate="focusout", validatecommand=(validatecommand, '%W', '%s', '%P' ), state=state )
		self.label_description.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.entry_value.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )


	def set_value(self, value):
		self.entry_value.delete(0,tk.END)
		self.entry_value.insert(0, str(value) )


	def get_value_string(self):
		return self.entry_value.get()


	def config_entry(self, state):
		self.entry_value.config(state=state)


##############################################################################

class PathSelectionWithDescription(tk.Frame):		# 21/1/2021, has to be tested

	def __init__(self, master, description="Descripcion", validatecommand=do_nothing, state='normal', initialdir="", relative_path=True ):
		tk.Frame.__init__(self, master )
		self.label_description = tk.Label(master=self,  text=description)

		self.frame_path_and_button = tk.Frame( master=self )
		self.frame_path_and_button.columnconfigure( 0 , weight=0, minsize=50)
		self.frame_path_and_button.columnconfigure( 1 , weight=1, minsize=50)
		self.entry_value = ttk.Entry(master=self.frame_path_and_button, validate="focusout", validatecommand=(validatecommand, '%W', '%s', '%P' ), state=state )
		self.button_choose_path = tk.Button(master=self.frame_path_and_button, text="Examinar", width=6, command = self.choose_button_callback )

		self.entry_value.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.button_choose_path.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )

		self.label_description.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.frame_path_and_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.initialdir = initialdir	# Store this for later usage
		self.relative_path = relative_path	# Store this for later usage



	def set_value(self, value):
		self.entry_value.delete(0,tk.END)
		self.entry_value.insert(0, str(value) )


	def get_value_string(self):
		return self.entry_value.get()


	def config_entry(self, state):
		self.entry_value.config(state=state)
		self.button_choose_path.config(state=state)


	def choose_button_callback(self):
		# The examine button has been clicked. A choose file dialog will appear....
		chosen_path = filedialog.askopenfilename(initialdir = self.initialdir, title = "Select file",filetypes = (("all files","*"),("all files with ext","*.*"),("jpeg files","*.jpg"),("png files","*.png")))
		# Manage the user file selection
		if isinstance( chosen_path, str ) and (chosen_path != ""):
			# Note: when <type 'str'> # File selected, OK clicked
			if self.relative_path == True:
				self.set_value(value=os.path.relpath( path=chosen_path, start=self.initialdir) )
			else:		# Absolute path
				self.set_value(value=chosen_path)
		#elif isinstance( chosen_new_game_path, unicode ):
			# Note: when<type 'unicode'> # Nothing selected, Cancel clicked
		#elif isinstance( chosen_new_game_path, tuple ):
			# Note: when <type 'tuple'> # File selected, Cancel clicked
			# Note: when <type 'tuple'> # Multiple files selected, OK clicked



		
