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

Support for other languages is implemented. The language can be selected from the preferences dialog. Supported languages are spanish, english and french. A [bash script](https://github.com/AlCastilloBa/roadcoin_level_editor/tree/master/locales/locales_mgmt_script) manages the creation and compilation of translation templates. New languages can be added easily.

# How to use this program

The program is started by running the ```rceditor_main.py``` file. The main user interface will be started.

This program is the level editor for the [roadcoin game](https://github.com/AlCastilloBa/roadcoin). Therefore, a copy of the game tree directory is required somewhere on the computer. On the preferences/settings dialog the root of the game tree must be set in order to be able to open and save levels correctly.

On the file menu, the standard file controls can be found (new, open, save, save as, etc). Possible options are to create a new empty map, or load an existing map.

There is a map viewer on the center of the main window. It can be controlled with the usual controls (for example, similar to a CAD program). The level coordinates will be shown on the right part of the status bar. The zoom can be adjusted either with the zoom button, or by pressing <kbd>Ctrl</kbd> and using the mousewheel. The level view can be panned with the mousewheel (on both axis).

The program is based on modes. The program can only be in one mode at a time. The current mode can be selected with the upper bar buttons. The explanation of the modes are as follows:

## General mode
This mode allows to set the general level properties (map name, description, coin start position, rotation type, etc). There is a button to choose the coin start position directly from the map viewer.

## Image mode
This mode allows to choose the images from the level (coin image, background, etc).

## Rotating Background mode
This mode allows to choose the rotating background properties (presence or not, image, and position). The rotation center can be chosen directly on the level viewer by using a button.

## Segment mode / Bumper mode / RACCZ mode
This mode allows to create, edit and delete line segments/pinball bumpers/"round acceleration zones" on the map. These are the primitive objects of the game:
* A line segment is a line that can be a wall, the level goal, or a hazard line.
* A pinball bumper represents a cylinder that kicks the ball from it.
* A round acceleration zone is a circle that creates a force that accelerates the coin in a direction.

The usage of each mode (segments/pinball bumpers/"round acceleration zones") are similar to each other. The selected mode implies which type of object can be created, selected or edited.

To create a new segment/bumper/RACCZ, press the *New* button on the left toolbar. The status bar (lower part of the window) will tell you the steps to be taken in order to create each object (usually by clicking on the level editor). The *Align* button allows to toggle a point search mode, that allows the mouse to travel to near points. If a near point is detected, it will be marked with a square indicator. This align mode is useful to create strings of connected segments (the start of one segment is the end of the previous one).

To edit the properties of an existing object, press the *Edit* button on the left toolbar and select an object on the level viewer. The selected object will be highlighted and its properties will be shown on the right frame of the window. At this point, this properties can be edited.

When an object is selected, it can be deleted by pressing the *Delete* button on the left toolbar.

On these modes, the object list can be shown and edited on a table format. In order to do this, press the *Table* button. This button will show or hide a new window with a table. The table window and the main editor window are completely synchronized (changes made on one window will reflect on the other). The table window has buttons to create and delete objects. Selecting an object on the editor selects the corresponding line on the table. Adding or removing objects on the main windows will update the table accordingly.


Once all the level has been edited, the map can be saved using the *Save As* in the *File* menu. This will create a file with all the settings and created objects. This level file can be added to the roadcoin game, or be opened again with the editor for further editing.
