
import bpy, platform, os

from bpy.types import Operator
from .texture_slots import FindMaterialSlotInName

def Find3DViewContext():
    """
    Builds and returns a context override for when you NEED TO MAKE SURE your operators
    are executing in a 3D View.
    """

    def getArea(type):
        for screen in bpy.context.workspace.screens:
            for area in screen.areas:
                if area.type == type:
                    return area

    # https://blender.stackexchange.com/questions/15118/how-do-i-override-context-for-bpy-ops-mesh-loopcut
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

class PAK_OT_CreateFileData(Operator):
    """Create a new empty object for which PakPal data is stored"""

    bl_idname = "pak.create_file_data"
    bl_label = "Create PakPal Data"

    def execute(self, context):

        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        try:
            file_data = bpy.data.objects[addon_prefs.default_datablock]
            return {'CANCELLED'}
        except:
            pass

        # Ensure we're in the right context before creating the datablock.
        override = Find3DViewContext()
        prev_mode = context.mode
        prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        with context.temp_override(
            screen = override['screen'],
            window = context.window_manager.windows[0], 
            area = override['area'], 
            region = override['region']
            ):

            if prev_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)  

            # Otherwise create the object using the addon preference data
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.ops.object.empty_add(type = 'CIRCLE') # apparently using plain axes causes a crash.

            default_datablock = bpy.context.view_layer.objects.active
            default_datablock.name = addon_prefs.default_datablock
            default_datablock.hide_viewport = True
            default_datablock.hide_render = True
            default_datablock.hide_select = True
            default_datablock.PAK_FileData.is_file_data = True

            context.view_layer.objects.active = prev_active_object
            for obj in prev_selected_objects:
                obj.select_set(state=True)

            # # Restore the context
            if prev_mode != 'OBJECT':

                # We need this because the context returns separate definitions.
                if prev_mode.find('EDIT') != -1:
                    prev_mode = 'EDIT'
                
                bpy.ops.object.mode_set(mode=prev_mode, toggle=False)

        self.report({'INFO'}, "PakPal data created.")
        return {'FINISHED'}

class PAK_OT_MultiSelect_Toggle(Operator):
    """
    A psuedo-operator for styling purposes, enables and disables multi-select toggle.
    """
    bl_idname = "scene.pak_multiselect_toggle"
    bl_label = "Enable Multiselect"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.enable_multiselect = not file_data.enable_multiselect
        return {'FINISHED'}

class PAK_OT_Bundles_Toggle(Operator):
    """
    A psuedo-operator for styling purposes, enables and disables multi-select toggle.
    """
    bl_idname = "scene.pak_bundles_toggle"
    bl_label = "Enable Bundles"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.enable_bundles = not file_data.enable_bundles
        return {'FINISHED'}

class PAK_OT_Refresh(Operator):
    """
    Refreshes the list of textures used in the current scene.
    """

    bl_idname = "scene.pak_refresh"
    bl_label = "Refresh List"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.is_internal_update = True

        bundles = file_data.bundles
        bundles.clear()

        if file_data.enable_bundles is False:
            
            for tex in bpy.data.images:
                bundle = bundles.add()
                bundle.name = tex.name
                bundle.enable_export = tex.PAK_Tex.enable_export
                bundle.export_location = tex.PAK_Tex.export_location
                bundle_item = bundle.bundle_items.add()
                bundle_item.tex = tex

        else:
            bundle_dict = {}

            for tex in bpy.data.images:
                filename = os.path.splitext(tex.name)[0]
                match = FindMaterialSlotInName(addon_prefs, filename)

                if match:
                    filename = filename.replace(match, "")
                
                if filename not in bundle_dict:
                    bundle_dict[filename] = []
                bundle_dict[filename].append(tex)

            for i, (name, textures) in enumerate(bundle_dict.items()):

                bundle = bundles.add()
                bundle.name = name
                bundle.enable_export = textures[0].PAK_Tex.enable_export
                bundle.export_location = textures[0].PAK_Tex.export_location
                
                for tex in textures:
                    bundle_item = bundle.bundle_items.add()
                    bundle_item.tex = tex
                
        file_data.bundles_list_index = 0
        file_data.is_internal_update = False
        
        return {'FINISHED'}


class PAK_OT_Show_Preferences(Operator):
    """Open a window to the PakPal Addon Preferences Menu"""
    bl_idname = "scene.pak_show_preferences"
    bl_label = "Show Addon Preferences"

    def execute(self, context):

        bpy.ops.screen.userpref_show()
        context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = "PakPal"


        return {'FINISHED'}



