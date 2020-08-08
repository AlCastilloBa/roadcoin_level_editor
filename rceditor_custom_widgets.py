import tkinter as tk
from tkinter import ttk		# Textbox


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

	def __init__(self, master, description="Descripcion", callback=do_nothing):
		tk.Frame.__init__(self, master )
		self.columnconfigure( 0 , weight=0, minsize=50)
		self.columnconfigure( 1 , weight=1, minsize=50)
		self.label_description = tk.Label(master=self,  text=description)
		self.entry_value = ttk.Entry(master=self, validate="focusout", validatecommand=callback )
		self.label_description.grid(row=0, column=0,  padx=2, pady=2, sticky="nsew" )
		self.entry_value.grid(row=0, column=1,  padx=2, pady=2, sticky="nsew" )


	def set_value(self, value):
		self.entry_value.delete(0,tk.END)
		self.entry_value.insert(0, str(value) )

		
