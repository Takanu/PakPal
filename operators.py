import bpy
from bpy.types import Menu, Panel, Operator, UIList

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
    """Create a new empty object for which Capsule data is stored and where both Active Export Presets and other scene data is stored"""

    bl_idname = "pak.create_file_data"
    bl_label = "Create Pak Data"

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
            bpy.ops.object.select_all(action ='DESELECT')
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

        self.report({'INFO'}, "Pak data created.")
        return {'FINISHED'}

class PAK_OT_Refresh(Operator):
    """Refreshes the list of textures used in the current scene."""

    bl_idname = "scene.pak_refresh"
    bl_label = "Refresh List"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except:
            return {'CANCELLED'}
        
        scene_data = context.scene.PAK_SceneData
        tex_list = scene_data.tex_list
        tex_list.clear()

        for tex in bpy.data.images:
            entry = tex_list.add()
            entry.tex = tex
        
        return {'FINISHED'}
    

class PAK_UL_TextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        # if file_data.enable_multiselect is True:
        #     layout.prop(item, "is_selected", text="", emboss=False)

        layout.prop(item.tex, "name", text="", emboss=False)
        layout.prop(item.tex.PAK_Tex, "enable_export", text="")

        


