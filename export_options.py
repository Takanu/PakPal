
import bpy
from bpy.types import Panel, Operator, UIList

from .main_menu import PAK_UI_CreatePakData, PAK_UI_CreateSelectionHeader

class PAK_PT_ExportOptionsMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Options"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 1

    def draw(self, context):

        layout = self.layout

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return
        
        selection_box = layout.box()
        selection_box_area = selection_box.column(align = True)
        selection_box_area.use_property_split = True
        selection_box_area.use_property_decorate = False

        PAK_UI_CreateSelectionHeader(selection_box_area, file_data)

        if len(file_data.bundles) > 0:
            if file_data.enable_multiselect:
                selection_box_area.prop(file_data, "proxy_enable_export")
                selection_box_area.separator()
                selection_box_area.prop(file_data, "proxy_export_location")
                selection_box_area.separator()
            else:
                entry = file_data.bundles[file_data.bundles_list_index]
                selection_box_area.prop(entry, "enable_export")
                selection_box_area.separator()
                selection_box_area.prop(entry, "export_location")
                selection_box_area.separator()
        
        texture_ops = layout.column(align = True)
        texture_ops.use_property_split = True
        texture_ops.use_property_decorate = False
        texture_ops.operator("pak.export_images", icon = 'EXPORT')
        texture_ops.separator()