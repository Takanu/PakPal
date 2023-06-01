import bpy, platform, os
from bpy.types import Operator
from bpy.props import EnumProperty

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
    """Create a new empty object for which Pak data is stored"""

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

        self.report({'INFO'}, "Pak data created.")
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
        
        file_data.is_internal_update = True
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
        
        file_data.is_internal_update = True
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
            bundle_strings = [t.text for t in addon_prefs.bundle_strings]

            for tex in bpy.data.images:
                filename = os.path.splitext(tex.name)[0]
                match = next(filter(filename.endswith, bundle_strings), None)

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

class PAK_OT_AddPath(Operator):
    """Create a new Export Location"""

    bl_idname = "scene.pak_addpath"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}

        new_path = file_data.locations.add()
        new_path.name = "Location " + str(len(file_data.locations))
        new_path.path = ""

        return {'FINISHED'}
    

class PAK_OT_DeletePath(Operator):
    """
    Delete the selected export location from the list.  This will 
    also set the export location of all textures that used this to 'None'
    """

    bl_idname = "scene.pak_deletepath"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}

        sel_index = file_data.locations_list_index

        # Ensure that any objects with a matching preset are set to None.
        # The index needs increasing by one as it doesnt include 'None'
        images = bpy.data.images
        for img in images:
            if img.PAK_Tex.export_location == str(sel_index + 1):
                img.PAK_Tex.export_location = '0'

        
        # TODO: Ensure the selection interface is updated so it gets the new value!
        # TODO: Ensure this is as efficient as it can be for large scenes
        
        # Once everything has been set, remove it.
        file_data.locations.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(file_data.locations) > 0 and sel_index != 0:
            file_data.locations_list_index -= 1
        

        return {'FINISHED'}

class PAK_OT_AddExportLocTag(Operator):
    """Add a new export location tag to the currently selected location.  These are used to auto-name file structures with information about the export like file name, time, etc"""

    bl_idname = "scene.pak_add_export_loc_tag"
    bl_label = "Add Export Location Tag"

    path_tags: EnumProperty(
        name = "Add Path Tag",
        description = "",
        items =  (
        # ('tex_name', 'Image Name', 'Adds a folder with the name of the Image being exported.'),
        ('blend_file_name', 'Blend File Name', 'Adds a folder with the blend file name.'),
        # ('export_preset_name', 'Export Preset Name', 'Adds a folder with the Export Preset name used on export.'),
        ('export_date_ymd', 'Export Date (Year-Month-Day)', 'Adds a folder with the date of the export.'),
        ('export_date_dmy', 'Export Date (Day-Month-Year)', 'Adds a folder with the date of the export.'),
        ('export_date_mdy', 'Export Date (Month-Year-Day)', 'Adds a folder with the date of the export.'),
        ('export_time_hm', 'Export Time (Hour-Minute)', 'Adds a folder with the time of the export.'),
        ('export_time_hms', 'Export Time (Hour-Minute-Second)', 'Adds a folder with the time of the export.'),
        ),
    )

    def execute(self, context):
        #print(self)

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        # get the selected path
        path_index = file_data.locations_list_index
        new_path = file_data.locations[path_index].path
        end_path = ""

        # directory failsafe
        if platform.system() == 'Windows':
            if new_path.endswith("\\") == False and new_path.endswith("//") == False:
                new_path += "\\"
            end_path = "\\"
        else:
            if new_path.endswith("/") == False:
                new_path += "/"
            end_path = "\\"

        # insert the selected option into the currently selected path
        new_path += "^"
        new_path += self.path_tags
        new_path += "^" + end_path
        
        file_data.locations[path_index].path = new_path

        return {'FINISHED'}


class PAK_OT_Show_Preferences(Operator):
    """Open a window to the Pak Addon Preferences Menu"""
    bl_idname = "scene.pak_show_preferences"
    bl_label = "Show Addon Preferences"

    def execute(self, context):

        bpy.ops.screen.userpref_show()
        context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = "Pak"


        return {'FINISHED'}

class PAK_OT_AddBundleString(Operator):
    """Add a bundle string to the list"""

    bl_idname = "scene.pak_addbundlestring"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        new_string = addon_prefs.bundle_strings.add()
        new_string.text = "BundleString" + str(len(addon_prefs.bundle_strings))

        return {'FINISHED'}
    

class PAK_OT_DeleteBundleString(Operator):
    """Delete the selected bundle string from the list."""

    bl_idname = "scene.pak_deletebundlestring"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        sel_index = addon_prefs.bundle_strings_list_index

        # Once everything has been set, remove it.
        addon_prefs.bundle_strings.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(addon_prefs.bundle_strings) > 0 and sel_index != 0:
            addon_prefs.bundle_strings_list_index -= 1
        

        return {'FINISHED'}

class PAK_OT_Tutorial_StoredPresets(Operator):
    """Open a message describing how Bundle Strings work"""
    bl_idname = "scene.cap_tut_bundlestrings"
    bl_label = ""

    def execute(self, context):

        def tutorial_layout(self, context):
            self.layout.label(text = "Bundle Strings let you identify suffixes in image naming schemes")
            self.layout.label(text = "so that Pak can bundle images together in the interface.")
            self.layout.label(text = "")
            self.layout.label(text = "Tick Enable Bundles in the main Properties UI to toggle this behaviour.")
            self.layout.label(text = "")
            self.layout.label(text = "NOTE - These are not case sensitive.")

        # Get the current export data
        bpy.context.window_manager.popup_menu(tutorial_layout, title="Stored Export Presets", icon='HELP')


        return {'FINISHED'}