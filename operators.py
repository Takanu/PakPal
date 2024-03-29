
import bpy, platform, os

from bpy.types import Operator
from .material_slots import FindMaterialSlotInName, CreateDefaultMaterialSlotNames
from .main_menu import CreatePakPreviewTexture

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
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name]
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

            pak_data_obj = bpy.context.view_layer.objects.active
            pak_data_obj.name = addon_prefs.pak_filedata_name
            pak_data_obj.hide_viewport = True
            pak_data_obj.hide_render = True
            pak_data_obj.hide_select = True
            pak_data_obj.PAK_FileData.is_file_data = True

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
    """Enables and disables multi-select in the main image list, letting you edit many different images or bundles at the same time"""
    bl_idname = "pak.toggle_multiselect"
    bl_label = "Toggle Multiselect"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.enable_multiselect = not file_data.enable_multiselect

        # Ensure export options for the UI proxy is reset to help communicate
        # that it is not reading the state of any individual item.
        file_data.is_internal_update = True
        
        if file_data.enable_multiselect is True:
            file_data.proxy_enable_export = False
            file_data.proxy_export_location = '0'
        
        file_data.is_internal_update = False

        return {'FINISHED'}

class PAK_OT_Bundles_Toggle(Operator):
    """Enable or disable Bundles.  This feature bundles together images that share the same base name but use material slot names so you can edit material images together, as well as perform image packing operations"""
    bl_idname = "pak.toggle_bundles"
    bl_label = "Toggle Bundles"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.enable_bundles = not file_data.enable_bundles
        return {'FINISHED'}
    

class PAK_OT_Refresh(Operator):
    """Refresh the list of textures used in the current scene.  You'll need to do this every time images are loaded or deleted outside of PakPal"""

    bl_idname = "pak.refresh_images"
    bl_label = "Refresh List"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        file_data.is_internal_update = True

        bundles = file_data.bundles
        bundles.clear()

        if file_data.enable_bundles is False:
            
            for tex in bpy.data.images:

                if tex.name.startswith(".") and file_data.show_hidden is False:
                    continue

                bundle = bundles.add()
                bundle.name = tex.name
                bundle.enable_export = tex.PAK_Img.enable_export
                
                #workaround for a strange assignment issue
                if tex.PAK_Img.export_location != "": 
                    bundle.export_location = tex.PAK_Img.export_location

                bundle_item = bundle.pak_items.add()
                bundle_item.tex = tex

        else:
            bundle_dict = {}

            for tex in bpy.data.images:
                
                if tex.name.startswith(".") and file_data.show_hidden is False:
                    continue
                
                name_parts = [n for n in os.path.splitext(tex.name)]
                filename = name_parts.pop(0)
                extension = ""
                for text in name_parts:
                    extension += text

                match = FindMaterialSlotInName(addon_prefs, filename, None,
                                               file_data.case_sensitive_matching)

                if match:
                    filename = filename.replace(match, "")
                
                if filename not in bundle_dict:
                    bundle_dict[filename] = []
                bundle_dict[filename].append(tex)

            for i, (name, textures) in enumerate(bundle_dict.items()):

                bundle = bundles.add()
                if len(textures) == 1:
                    bundle.name = textures[0].name
                else:
                    bundle.name = name
                bundle.enable_export = textures[0].PAK_Img.enable_export

                #workaround for a strange enum assignment issue
                if textures[0].PAK_Img.export_location != "": 
                    bundle.export_location = textures[0].PAK_Img.export_location
                
                for tex in textures:
                    bundle_item = bundle.pak_items.add()
                    bundle_item.tex = tex
                
        if len(file_data.bundles) <= (file_data.bundles_list_index - 1):
            file_data.bundles_list_index = len(file_data.bundles) - 1
        file_data.is_internal_update = False
        
        return {'FINISHED'}

class PAK_OT_Delete_Images(Operator):
    """Deletes the selected images and purges them from the .blend file"""
    bl_idname = "pak.delete_selected_images"
    bl_label = "Delete Selected Images"
    bl_options = {'REGISTER', 'INTERNAL'}

    # https://blender.stackexchange.com/questions/73286/how-to-call-a-confirmation-dialog-box

    @classmethod
    def poll(cls, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
            return GetSelectionCount(file_data)
        except:
            return False
        # return True

    def execute(self, context):
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        image_count = GetSelectionCount(file_data)

        if image_count == 0:
            self.report({'WARNING'}, "No images were selected.")
            return {'FINISHED'}
        
        
        # Get the selected bundles and remove them from the collection
        selected_bundles = GetSelection(file_data)
        selected_images = [[pak_items.tex for pak_items in bundle.pak_items]
                            for bundle in selected_bundles]
        selected_images = set(i for j in selected_images for i in j)

        # Used to decrease the selected bundle.
        index_subtract = 0
        
        ## BUG - Removing by index doesn't appear to properly work, the items removed
        ## be at random rather than the correct index, I can't find a replicatable pattern.
        ##
        ## The bundle list will be regenerated instead.

        # for bundle in selected_bundles:
        #     for bundle in selected_bundles:
        #         print(file_data.bundles.find(bundle.name))
        #     print('-'*10)
            
        #     index = file_data.bundles.find(bundle.name)
        #     file_data.bundles.remove(index - index_subtract)

        #     if index <= file_data.bundles_list_index:
        #         index_subtract += 1
        
        # return {'FINISHED'}

        # Now purge the data
        bpy.data.batch_remove([image for image in selected_images if image is not None])
        self.report({'INFO'}, str(image_count) + " image(s) were deleted.")

        # TODO - Get the original solution working again to prevent potential slowdown in
        # large projects.
        bpy.ops.pak.refresh_images()

        # Decrement the index unless it would be less than zero
        file_data.bundles_list_index = max(0, (file_data.bundles_list_index - index_subtract))
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        layout = self.layout

        selected_images = GetSelectionCount(file_data)
        count = selected_images

        if selected_images == 0:
            layout.label(text = "At least one image/bundle must be selected.")

        else:
            layout.label(text = "This will delete and purge " + str(count) + " image(s) from the Blend file.")
            layout.label(text = "Any images selected with a Fake User will also be deleted.")
            layout.label(text = "Click OK to continue, or anywhere else to cancel.")

class PAK_OT_Show_Preferences(Operator):
    """Open a window to the PakPal Addon Preferences Menu"""
    bl_idname = "pak.show_preferences"
    bl_label = "Show Addon Preferences"

    def execute(self, context):

        bpy.ops.screen.userpref_show()
        context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = "PakPal"


        return {'FINISHED'}


class PAK_OT_Reset_Properties(Operator):
    """Resets PakPal properties for all images and clears the bundles, export locations and material slot names lists"""
    bl_idname = "pak.reset_properties"
    bl_label = "Reset Main Properties"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
                
        for image in bpy.data.images:
            image.PAK_Img.enable_export = False
            image.PAK_Img.export_location = '0'
        
        file_data.bundles.clear()
        file_data.bundles_list_index = 0
        file_data.locations.clear()
        file_data.locations_list_index = 0
        addon_prefs.material_slot_names.clear()
        addon_prefs.material_slot_names_list_index = 0

        # TODO: Find a way to completely reset collection properties
        file_data.preview_tex = None
        bpy.data.batch_remove(bpy.data.textures['PakPal Preview'])

        CreateDefaultMaterialSlotNames()
        CreatePakPreviewTexture()

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        layout = self.layout

        layout.label(text = "This will clear all PakPal data from all images.")
        layout.label(text = "It will also empty export location and texture slot lists.")
        layout.label(text = "Click OK to continue, or anywhere else to cancel.")

        
        return {'FINISHED'}

def GetSelection(file_data):
    # Used to return the bundles selected.
    if file_data.enable_multiselect is True:
        return [bundle for bundle in file_data.bundles 
                if bundle.is_selected]
    else:
        return [file_data.bundles[file_data.bundles_list_index]]

def GetSelectionCount(file_data):
    # Used to return the number of selected bundles.
    i = 0
    if file_data.enable_multiselect is True:
        bundle_list = [bundle.pak_items for bundle in file_data.bundles 
                        if bundle.is_selected]
        selected_images = set(i for j in bundle_list for i in j)
        return len(selected_images)

    elif len(file_data.bundles) > 0:
        return len(file_data.bundles[file_data.bundles_list_index].pak_items)

