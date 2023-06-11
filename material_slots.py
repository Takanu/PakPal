import bpy, os
from bpy.types import Panel, Operator, UIList

from .main_menu import PAK_UI_CreatePakData


def GetMaterialSlotStrings(addon_prefs):
    return [t.text for t in addon_prefs.material_slot_names]

# This ensures the search is done in a way that ignores cases.
def FindMaterialSlotInName(addon_prefs, filename, custom_slots = None):
    
    result = None
    slots = None
    if custom_slots is None:
        slots = GetMaterialSlotStrings(addon_prefs)
    else:
        slots = custom_slots

    filename = os.path.splitext(filename)[0]
    file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData

    if file_data.case_sensitive_matching is True:
        result = next(filter(filename.endswith, slots), None)

    else:
        for slot in slots:
            if slot in filename:
                result = slot
            elif slot.casefold() in filename.casefold():
                result = slot.casefold()
    
    return result


class PAK_OT_AddMaterialSlotName(Operator):
    """Add a material slot name to the list"""

    bl_idname = "pak.add_material_slot_name"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        new_string = addon_prefs.material_slot_names.add()
        new_string.text = "MaterialSlot" + str(len(addon_prefs.material_slot_names))

        return {'FINISHED'}
    

class PAK_OT_DeleteMaterialSlot(Operator):
    """Delete the selected material slot name from the list."""

    bl_idname = "pak.del_material_slot_name"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except:
            return {'CANCELLED'}

        sel_index = addon_prefs.material_slot_names_list_index

        # Once everything has been set, remove it.
        addon_prefs.material_slot_names.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(addon_prefs.material_slot_names) > 0 and sel_index != 0:
            addon_prefs.material_slot_names_list_index -= 1
        

        return {'FINISHED'}

class PAK_OT_MeterialSlots_Tutorial(Operator):
    """Open a message describing how material slot Names work"""
    bl_idname = "pak.show_material_slot_tutorial"
    bl_label = ""

    def execute(self, context):

        def tutorial_layout(self, context):
            self.layout.label(text = "Material slot names allow PakPal to automatically identify and bundle")
            self.layout.label(text = "material image sets together in the interface, as well as to")
            self.layout.label(text = "perform image packing operations on them.")
            self.layout.label(text = "")
            self.layout.label(text = "To enable Bundles, click on the 'image stack' icon next to")
            self.layout.label(text = "PakPal's image list interface.")

        # Get the current export data
        bpy.context.window_manager.popup_menu(tutorial_layout, title="Material Slot Name Info", icon='HELP')


        return {'FINISHED'}
    
class PAK_UL_MaterialSlotList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "text", text = "", emboss = False)

class PAK_PT_MaterialSlotMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Material Slot Names"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 4

    def draw_header_preset(self, _context):
        self.layout.operator("pak.show_material_slot_tutorial", 
                      text = "", icon = "HELP", emboss = False)

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
        texture_slot_names_list.template_list("PAK_UL_MaterialSlotList", "default", 
                                              addon_prefs, "material_slot_names", 
                                              addon_prefs, "material_slot_names_list_index", 
                                              rows = 6, maxrows = 12)
        texture_slot_names_list.separator()

        texture_slot_names_ops = texture_slot_names_area.column(align = True)
        texture_slot_names_ops.operator("pak.add_material_slot_name", text= "", icon = "ADD")
        texture_slot_names_ops.operator("pak.del_material_slot_name", text= "", icon = "REMOVE")
        
        material_slot_options = layout.row(align = False)
        # material_slot_options.use_property_split = True
        # material_slot_options.use_property_decorate = False
        material_slot_options.alignment = "CENTER"
        material_slot_options.prop(file_data, 'case_sensitive_matching')