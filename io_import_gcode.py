# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

## blendish python ripped from fro io_import_dxf

import bpy 

bl_info = {
    'name': 'Import GCode for FDM .gcode',
    'author': 'Simon Kirkby',
    'version': (0,0,3),
    'blender': (2, 5, 6),
    'api': 32738,
    'location': 'File > Import-Export > Gcode',
    'description': 'Import gcode files for reprap FDM printers .gcode',
    'warning': 'may not work',
    "wiki_url": "",
    "tracker_url": "",
    'category': 'Import-Export'}

__version__ = '.'.join([str(s) for s in bl_info['version']])

# gcode parser for blender 2.5 
# Simon Kirkby
# 201102051305
# tigger@interthingy.com 

#modified by David Anderson to handle Skeinforge comments
# Thanks Simon!!!

# modified by Alessandro Ranellucci (2011-10-14)
# to make it compatible with Blender 2.59
# and with modern 5D GCODE

import string,os
import bpy
import mathutils

#file_name ='/home/zignig/cube_export.gcode'
#file_name = 'c:/davelandia/blender/bre_in.gcode'

extrusion_diameter = 0.4


class tool:
    def __init__(self,name='null tool'):
        self.name = name

class move():
    def __init__(self,pos):
        self.pos = pos
        p = []
        p.append(self.pos['X'])
        p.append(self.pos['Y'])
        p.append(self.pos['Z'])
        self.point = p
    
class fast_move(move):
    def __init__(self,pos):
        move.__init__(self,pos)
        
class tool_on:
    def __init__(self,val):
        pass

class tool_off:
    def __init__(self,pos):
        self.pos = pos
        p = []
        p.append(self.pos['X'])
        p.append(self.pos['Y'])
        p.append(self.pos['Z'])
        self.point = p

class setLayerHeight:
    def __init__(self,val):
        print('Got layer height: ')
        print(val)
        pass

class setExtrusionWidth:
    def __init__(self,val):
        print('Got extrusion width')
        print(val)
        pass

class layer:
    def __init__(self):
        print('layer')
        pass

class setting:
    def __init__(self,val):
        pass

class set_temp(setting):
    def __init__(self,val):
        setting.__init__(self,val)
 
class tool_change():
    def __init__(self,val):
        self.val = val

class undef:
    def __init__(self,val):
        pass


codes = {
    '(':{
        '</surroundingLoop>)' : undef,
        '<surroundingLoop>)' : undef,
        '<boundaryPoint>' : undef,
        '<loop>)' : undef,
        '</loop>)' : undef,
        '<layer>)' : setLayerHeight,
        '</layer>)' : undef,
        '<layer>' : undef,
        '<layerThickness>' : setLayerHeight,
        '</layerThickness>)' : undef,
        '<perimeter>)' : undef,
        '</perimeter>)' : undef, 
        '<bridgelayer>)' : undef,
        '</bridgelayer>)' : undef,
        '</extrusion>)' : undef,
        '<perimeterWidth>' : setExtrusionWidth,
        '</perimeterWidth>)' : undef
    
    },    
    'G':{
        '0': move,
        '1': move,
        '01' : move
        
    },
    'M':{
        '101' : tool_on,
        '103' : tool_off
        
    }
}

class driver:
    # takes action object list and runs through it 
    def __init__(self):
        pass
    
    def drive(self):
        pass 
    
    def load_data(self,data):
        self.data = data

    
def vertsToPoints(Verts):
    # main vars
    vertArray = []
    for v in Verts:
        vertArray += v
        vertArray.append(0)
    return vertArray

def create_poly(verts,counter):
    name = 'skein'+str(counter) 
    pv = vertsToPoints(verts)
    # create curve
    scene = bpy.context.scene
    newCurve = bpy.data.curves.new(name, type = 'CURVE')
    newSpline = newCurve.splines.new('POLY')
    #newSpline.use_cyclic_v = True #Not really needed and takes up a TON of CPU
    newSpline.points.add(int((len(pv)/4) - 1))
    newSpline.points.foreach_set('co',pv)
    newSpline.use_endpoint_u = True
    
    # create object with newCurve
    newCurve.bevel_object = bpy.data.objects['profile']
    newCurve.dimensions = '3D'
    new_obj = bpy.data.objects.new(name, newCurve) # object
    scene.objects.link(new_obj) # place in active scene
    return new_obj
    
class blender_driver(driver):
     def __init__(self):
         driver.__init__(self)
         
     def drive(self):

    
        
        print('building curves')
        # info 
        count = 0 
        for i in self.data:
            if isinstance(i,layer):
                count += 1
        print('has '+str(count)+' layers')
        
        
        print('createing poly lines')
        if 'profile' in bpy.data.objects:
            print('profile exists')
        else:
            bpy.ops.curve.primitive_bezier_circle_add()
            curve = bpy.context.selected_objects[0]
            d = extrusion_diameter
            curve.scale = [d,d,d]
            curve.name = 'profile'
            curve.data.resolution_u = 2
            curve.data.render_resolution_u = 2
            
        poly = []
        lastPoint = []
        layers = []
        this_layer = []
        counter = 1
        global thing
        for i in self.data:
            if isinstance(i,move):
                poly.append(i.point)
            if isinstance(i,tool_off):
                poly.insert(0,lastPoint)    #Prepend the poly with the last point before the extruder was turned on
                if len(poly) > 1:           #A poly is only a poly if it has more than one point!
                    counter += 1
                    print('Creating poly ' + str(counter))
                    pobj = create_poly(poly,counter)
                    this_layer.append(pobj)
                else:                       #This is not a poly! Discard!
                    print('Discarding bad poly')
                poly = []
                lastPoint = i.point         #Save this point, it might become the start of the next poly
            if isinstance(i,layer):
                print('layer '+str(len(layers)))
                layers.append(this_layer)
                this_layer = []
        layers.append(this_layer)
        
        print('animating build')
        
        s = bpy.context.scene
        # make the material 
        if 'Extrusion' in bpy.data.materials:
            mt = bpy.data.materials['Extrusion']
        else:
            # make new material
            bpy.ops.material.new()
            mt = bpy.data.materials[-1]
            mt.name = 'Extrusion'
        
        s.frame_end = len(layers)
        # hide everything at frame 0
        s.frame_set(0)
        
        for i in range(len(layers)):
            for j in layers[i]:
                j.hide = True
                j.hide_render = True
                j.keyframe_insert("hide")
                j.keyframe_insert("hide_render")
                # assign the material 
                j.active_material = mt
        
        # go through the layers and make them reappear
        for i in range(len(layers)):
            s.frame_set(i)
            print('frame '+str(i))
            for j in layers[i]:
                j.hide = False
                j.hide_render = False
                j.keyframe_insert("hide")
                j.keyframe_insert("hide_render")


class machine:
    
    extruder = False
    
    extrusionSize = []

    def __init__(self,axes):
        self.axes = axes
        self.axes_num = len(axes)
        self.data = []
        self.cur = {} 
        self.tools = []
        self.commands = []
        self.driver = driver()

    def add_tool(self,the_tool):
        self.tools.append(the_tool)
        
    def remove_comments(self):
        tempd=[]
        for st in self.data:
            startcommentidx= st.find('(')
            if startcommentidx == 0 :  #line begins with a comment 
                split1=st.partition(')')
                st = ''
            if startcommentidx > 0:   # line has an embedded comment to remove
                split1=st.partition('(')
                split2=split1[2].partition(')')
                st = split1[0]+split2[2]
            if st != '':    
                tempd.append(st)
            #print("...>",st)
        self.data=tempd
        
    

    def import_file(self,file_name):
        print('opening '+file_name)
        f = open(file_name)
        #for line in f:
        #    self.data.append(self.remove_comments(line))
        self.data=f.readlines()
        f.close()
        self.remove_comments()
        
        # uncomment to see the striped file
        #k = open('c:/davelandia/blender/out1.txt','w')
        #k.writelines(self.data)
        #k.close()
        
        print(str(len(self.data))+' lines')
        
                

    def process(self):
        # zero up the machine
        pos = {}
        for i in self.axes:
            pos[i] = 0
            self.cur[i] = 0 #init
        for i in self.data: #get data
            i=i.strip() #clean (Is there a better way?)
            print( "Parsing Gcode line ", i)
            #print('pos: ' + pos)
            tmp = i.split()
            command = tmp[0][0]
            com_type = tmp[0][1:]
            if command in codes:
                if com_type in codes[command]:
                    print('good com =>'+command+com_type)
                    
                    for j in tmp[1:]:
                        axis = j[0]
                        if axis == ';':
                            # ignore comments
                            break
                        if axis in self.axes:
                            val = float(j[1:])
                            pos[axis] = val
                            if self.cur['Z'] != pos['Z']:
                                self.commands.append(layer())
                                self.commands.append(tool_off(pos))
                            self.cur[axis] = val
                    # create action object
                    #print(pos)
                    
                    if (command != '('):
                        #We have a GCode (Not a skeinforge command)
                        if com_type == '101':
                            machine.extruder = True
                            print('Extruder ON')
                    
                        elif com_type == '103':
                            machine.extruder = False
                            print('Extruder OFF')
                                
                        elif (machine.extruder == False):
                            act = tool_off(pos)
                            print('made move with extruder OFF')
                            self.commands.append(act)
                        else:
                            act = codes[command][com_type](pos)
                            print('made move with extruder ON')
                            self.commands.append(act)
                    else:
                        #We have a skeinforge command
                        codes [command] [com_type] (tmp[2])

                else:
                    print(i)
                    print(' G/M/T Code for this line is unknowm ' + com_type)
                    
                #elif commmand[0] in codes: #We got a probable skeinforge command!
                        #if command[1:] in codes [command[0]]:
                        #We did get a skeinforge command!
                        #codes command[0] command[1: ] (pos)
                        #print('Got a skeinforge command!')
            
            else:
                print(' line does not have a G/M/T Command '+ str(command))


def import_gcode(file_name):
    print('hola')
    m = machine(['X','Y','Z'])
    m.import_file(file_name)
    m.process()
    d = blender_driver()
    d.load_data(m.commands)
    d.drive()
    print('finished parsing... done')


DEBUG= False
from bpy.props import *

def tripleList(list1):
    list3 = []
    for elt in list1:
        list3.append((elt,elt,elt))
    return list3

theMergeLimit = 4
theCodec = 1 
theCircleRes = 1

class IMPORT_OT_gcode(bpy.types.Operator):
    '''Imports Reprap FDM gcode'''
    bl_idname = "import_scene.gocde"
    bl_description = 'Gcode reader, reads tool moves and animates layer build'
    bl_label = "Import gcode" +' v.'+ __version__
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filepath = StringProperty(name="File Path", description="Filepath used for importing the GCode file", maxlen= 1024, default= "")

    #new_scene = BoolProperty(name="Replace scene", description="Replace scene", default=toggle&T_NewScene)
    #new_scene = BoolProperty(name="New scene", description="Create new scene", default=toggle&T_NewScene)
    #curves = BoolProperty(name="Draw curves", description="Draw entities as curves", default=toggle&T_Curves)
    #thic_on = BoolProperty(name="Thic ON", description="Support THICKNESS", default=toggle&T_ThicON)
#
 #   merge = BoolProperty(name="Remove doubles", description="Merge coincident vertices", default=toggle&T_Merge)
 #   mergeLimit = FloatProperty(name="Limit", description="Merge limit", default = theMergeLimit*1e4,min=1.0, soft_min=1.0, max=100.0, soft_max=100.0)

 #   draw_one = BoolProperty(name="Merge all", description="Draw all into one mesh-object", default=toggle&T_DrawOne)
 #   circleResolution = IntProperty(name="Circle resolution", description="Circle/Arc are aproximated will this factor", default = theCircleRes,
 #               min=4, soft_min=4, max=360, soft_max=360)
 #   codecs = tripleList(['iso-8859-15', 'utf-8', 'ascii'])
 #   codec = EnumProperty(name="Codec", description="Codec",  items=codecs, default = 'ascii')

 #   debug = BoolProperty(name="Debug", description="Unknown DXF-codes generate errors", default=toggle&T_Debug)
 #   verbose = BoolProperty(name="Verbose", description="Print debug info", default=toggle&T_Verbose)

    ##### DRAW #####
    def draw(self, context):
        layout0 = self.layout
        #layout0.enabled = False

        #col = layout0.column_flow(2,align=True)
#        layout = layout0.box()
#        col = layout.column()
#        #col.prop(self, 'KnotType') waits for more knottypes
#        #col.label(text="import Parameters")
#        #col.prop(self, 'replace')
#        col.prop(self, 'new_scene')
#        
#        row = layout.row(align=True)
#        row.prop(self, 'curves')
#        row.prop(self, 'circleResolution')
#
#        row = layout.row(align=True)
#        row.prop(self, 'merge')
#        if self.merge:
#            row.prop(self, 'mergeLimit')
 
#        row = layout.row(align=True)
        #row.label('na')
#        row.prop(self, 'draw_one')
#        row.prop(self, 'thic_on')
#
#        col = layout.column()
#        col.prop(self, 'codec')
# 
#        row = layout.row(align=True)
#        row.prop(self, 'debug')
#        if self.debug:
#            row.prop(self, 'verbose')
#         
    def execute(self, context):
        global toggle, theMergeLimit, theCodec, theCircleRes
        #O_Merge = T_Merge if self.properties.merge else 0
        #O_Replace = T_Replace if self.properties.replace else 0
        #O_NewScene = T_NewScene if self.properties.new_scene else 0
        #O_Curves = T_Curves if self.properties.curves else 0
        #O_ThicON = T_ThicON if self.properties.thic_on else 0
        #O_DrawOne = T_DrawOne if self.properties.draw_one else 0
        #O_Debug = T_Debug if self.properties.debug else 0
        #O_Verbose = T_Verbose if self.properties.verbose else 0

        #toggle =  O_Merge | O_DrawOne | O_NewScene | O_Curves | O_ThicON | O_Debug | O_Verbose
        #theMergeLimit = self.properties.mergeLimit*1e-4
        #theCircleRes = self.properties.circleResolution
        #theCodec = self.properties.codec

        import_gcode(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(IMPORT_OT_gcode.bl_idname, text="Reprap GCode (.gcode)", icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

