Blender GCode Reader Add-on 
===========================
Reads Reprap and Makerbot gcode files into blender 2.6 for rendering and visualization

History:
--------
Modified by Alessandro Ranellucci (2011-10-14)
to make it compatible with Blender 2.59
and with modern 5D GCODE

Modified by Winter Guerra (XtremD) on February 16th, 2012
to make the script compatable with stock Makerbot GCode files
and grab all nozzle extrusion information from Skeinforge's machine output
WARNING: This script no longer works with stock 5D GCode! (Can somebody please integrate the two versions together?)
A big shout-out goes to my friend Jon Spyreas for helping me block-out the maths needed in the "addArc" subroutine
Thanks a million dude!
Github branch link: https://github.com/xtremd/blender-gcode-reader


Original developer:
-------------------
Simon Kirkby
tigger@interthingy.com

Instructions:
-------------
1. Get latest version of Blender here: http://www.blender.org/download/get-blender/

2. Open Blender

3. Navigate to:
	File Menu
	User Preferences (CTL-ALT-U)
	Select The Add-Ons Tab
	Press the Install Add-On Button ( down the bottom )
	Select the python script in the file browser
	CLick the "Enable Add-on" checkbox to the right of the Add-on slot 
	Click "Save As Default" if you want the Add-on to always be available

4. Import your GCode file for visualization: File-> Import -> Gcode
	Select a file and watch the console for progress. The import process is VERY CPU intensive and may take a long time.
	Having a computer with lots of RAM might help speed up the process considerably.

5. Bask in the glory of your awesome small plastic thing.

Simon
