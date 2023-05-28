import bpy, os, platform
from bpy.types import Operator

from .paths import *

def FindImageContext():
    """
    Builds and returns a context override for when you NEED TO MAKE SURE your operators
    are executing in an Image context.
    """

    def getArea(type):
        for screen in bpy.context.workspace.screens:
            for area in screen.areas:
                if area.type == type:
                    return area

    win      = bpy.context.window
    scr      = win.screen
    areas3d  = [getArea('VIEW_3D')]
    region   = [region for region in areas3d[0].regions if region.type == 'WINDOW']

    override = {'window':win,
                'screen':scr,
                'area'  :getArea('VIEW_3D'),
                'region':region[0],
                'scene' :bpy.context.scene,
                'space' :getArea('VIEW_3D').spaces[0],
                }
    
    return override

class PAK_OT_Export(Operator):
    """Exports all images marked for export."""

    bl_idname = "scene.pak_export"
    bl_label = "Export Images"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        
        for tex_item in file_data.textures:
            if tex_item.tex.PAK_Tex.enable_export:
                tex = tex_item.tex
                location_index = int(tex.PAK_Tex.export_location) - 1
                location = file_data.locations[file_data.locations_list_index]

                path = CreateFilePath(location, tex, True)
                name = SubstituteNameCharacters(tex.name)

                tex.save(filepath = path + name)
        
        return {'FINISHED'}

