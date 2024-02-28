
import bpy
import mathutils

from bpy.types import Menu, Panel, Operator, UIList
from .main_menu import PAK_UI_CreatePakData
from .image_format_properties import PAK_ImageFormat, UI_CreateFormatSettings

# https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html#imageformatsettings-bpy-struct

# NOTE: Color management has been disabled for now, color alteration
# is removed when creating and rendering new images.

# NOTE: Setting transfers must be verified before use, as switching formats
# can make some options invalid and the user might not realize it.


def UI_CreateFormatData(layout):

    # UI Prompt for when the PakPal file data can no longer be found.
    format_box = layout.box()
    format_info = format_box.column(align = True)
    format_info.label(text = "PakPal image format settings cannot be found.",
                      icon = "ERROR")
    
    format_desc = layout.column(align = True)
    format_desc.separator()
    format_desc.label(text = "You might have deleted the scene it was stored in (thats fine!)")
    format_desc.label(text = "Press the button below to rebuild this data in the current scene.")
    format_desc.separator()

    format_desc.separator()
    format_desc.operator("pak.create_image_format_data")

    return



class PAK_OT_AddFormat(Operator):
    """Create a new Export Format"""

    bl_idname = "scene.pak_addformat"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        new_path = file_data.formats.add()
        new_path.name = "Format " + str(len(file_data.formats))

        return {'FINISHED'}
    

class PAK_OT_DeleteFormat(Operator):
    """
    Delete the selected export format from the list.  This will 
    also set the export format of all textures that used this to 'None'
    """

    bl_idname = "scene.pak_deleteformat"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        sel_index = file_data.formats_list_index

        # Ensure that any objects with a matching preset are set to None.
        # The index needs increasing by one as it doesnt include 'None'
        images = bpy.data.images
        for img in images:
            if img.PAK_Img.export_format == str(sel_index + 1):
                img.PAK_Img.export_format = '0'

        
        # TODO: Ensure the selection interface is updated so it gets the new value!
        # TODO: Ensure this is as efficient as it can be for large scenes
        
        # Once everything has been set, remove it.
        file_data.formats.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(file_data.formats) > 0 and sel_index != 0:
            file_data.formats_list_index -= 1
        

        return {'FINISHED'}

class PAK_UL_ExportFormatList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        layout.prop(item, "name", text="", emboss=False)

class PAK_PT_ExportFormatMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Formats"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 3

    # def draw_header_preset(self, _context):
    #     self.layout.operator("pak.show_material_slot_tutorial", 
    #                   text = "", icon = "HELP", emboss = False)

    def draw(self, context):
        
        layout = self.layout

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return

        format_list = layout.row(align= True)
        format_list.template_list("PAK_UL_ExportFormatList", "default", file_data, 
                                   "formats", file_data, "formats_list_index", 
                                   rows = 3, maxrows = 6)
        format_list.separator()

        format_ops = format_list.column(align= True)
        format_ops.operator("scene.pak_addformat", text = "", icon = "ADD")
        format_ops.operator("scene.pak_deleteformat", text = "", icon = "REMOVE")

        format_info = layout.column(align = False)
        format_info.use_property_split = True
        format_info.use_property_decorate = False
        format_info.separator()

        count = 0
        for i, item in enumerate(file_data.formats, 1):
            count += 1

        if file_data.formats_list_index > -1 and file_data.formats_list_index < count:
            current_format = file_data.formats[file_data.formats_list_index]

            UI_CreateFormatSettings(format_info, current_format)
            format_info.separator()
