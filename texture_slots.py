import bpy
from bpy.types import Panel, Operator, UIList

from .main_menu import PAK_UI_CreatePakData

class PAK_OT_AddTextureSlotName(Operator):
    """Add a texture slot name to the list"""

    bl_idname = "scene.pak_add_textureslotname"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        new_string = addon_prefs.texture_slot_names.add()
        new_string.text = "TextureSlot" + str(len(addon_prefs.texture_slot_names))

        return {'FINISHED'}
    

class PAK_OT_DeleteTextureSlot(Operator):
    """Delete the selected texture slot name from the list."""

    bl_idname = "scene.pak_del_textureslotname"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        sel_index = addon_prefs.texture_slot_names_list_index

        # Once everything has been set, remove it.
        addon_prefs.texture_slot_names.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(addon_prefs.texture_slot_names) > 0 and sel_index != 0:
            addon_prefs.texture_slot_names_list_index -= 1
        

        return {'FINISHED'}

class PAK_OT_Tutorial_StoredPresets(Operator):
    """Open a message describing how Texture Slot Names work"""
    bl_idname = "scene.cap_tut_bundlestrings"
    bl_label = ""

    def execute(self, context):

        def tutorial_layout(self, context):
            self.layout.label(text = "Texture slot names let you identify suffixes in image naming schemes")
            self.layout.label(text = "so that Pak can bundle images together to make image sets easier")
            self.layout.label(text = "to manage, and to perform image pack operations.")
            self.layout.label(text = "")
            self.layout.label(text = "Tick Enable Bundles under the image list to toggle this behaviour.")
            self.layout.label(text = "")
            self.layout.label(text = "NOTE - These are not case sensitive.")

        # Get the current export data
        bpy.context.window_manager.popup_menu(tutorial_layout, title="Stored Export Presets", icon='HELP')


        return {'FINISHED'}
    
class PAK_UL_TextureSlotList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "text", text = "", emboss = False)

class PAK_PT_TextureSlotMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Texture Slots"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 3

    def draw_header_preset(self, _context):
        layout = self.layout
        icon = layout.row(align = True)
        icon.operator("scene.cap_tut_bundlestrings", text = "", icon = "HELP")

    def draw(self, context):
        
        layout = self.layout

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return

        texture_slot_names_area = layout.row(align = False)
        texture_slot_names_list = texture_slot_names_area.column(align = True)
        texture_slot_names_list.template_list("PAK_UL_TextureSlotList", "default", 
                                              addon_prefs, "texture_slot_names", 
                                              addon_prefs, "texture_slot_names_list_index", 
                                              rows = 3, maxrows = 6)
        texture_slot_names_list.separator()

        texture_slot_names_ops = texture_slot_names_area.column(align = True)
        texture_slot_names_ops.operator("scene.pak_add_textureslotname", text= "", icon = "ADD")
        texture_slot_names_ops.operator("scene.pak_del_textureslotname", text= "", icon = "REMOVE")
        
        