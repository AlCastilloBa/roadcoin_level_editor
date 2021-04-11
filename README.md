# roadcoin_level_editor
(WIP) Level editor for roadcoin

# Description

Level editor for [roadcoin game](https://github.com/AlCastilloBa/roadcoin). It will help the creation and edition of new levels, using a graphical editor.

| ![Screenshot_001](/images/screenshots/screenshot_001.png) |
|---------------------------------------------------------- |
|![Screenshot_003](/images/screenshots/screenshot_003.png)  |
| ----------------------------------------------------------|
| ![Screenshot_002](/images/screenshots/screenshot_002.png) | 

# Technical details

Uses python 3 and Tkinter for building the user interface. The graphical viewer window is created using a Tkinter canvas. The aim is to get a simple and minimal, but functional interface.

Tested on Python 3.7.7, under GNU/Linux. Other versions or operating systems not tested yet.

In order to run this program, the following packages are required:
* Python 3 (with Tkinter support)
* Logging package
* Pillow package
* Gettext package

# Current status

Currently on the final stages of development. The application can load and show maps, the panning and zooming is operational. Items can be selected and modified directly on the editor window. New items can be added, by pointing and clicking directly on the viewer window. Additionally, tables can be used for editing. Properties can be modified, and levels can be saved.

The required funcitonality for editing is implemented. The application is currently being used to create new levels. Intense debugging is expected at this stage.

Support for other languages is yet to be implemented.

# How to use this program

The program is started by running the ```rceditor_main.py``` file. The main user interface will be started.

This program is the level editor for the [roadcoin game](https://github.com/AlCastilloBa/roadcoin). Therefore, a copy of the game tree directory is required somewhere on the computer. On the preferences/settings dialog the root of the game tree must be set in order to be able to open and save levels correctly.

On the file menu, the standard file controls can be found (new, open, save, save as, etc). Possible options are to create a new empty map, or load an existing map.

There is a map viewer on the center of the main window. It can be controlled with the usual controls (for example, similar to a CAD program). The level coordinates will be shown on the right part of the status bar. The zoom can be adjusted either with the zoom button, or by pressing <kbd>Ctrl</kbd> and using the mousewheel. The level view can be panned with the mousewheel (on both axis).

The program is based on modes. The program can only be in one mode at a time. The current mode can be selected with the upper bar buttons. The explanation of the modes are as follows:


