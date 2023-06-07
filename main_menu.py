import bpy
from bpy.types import Menu, Panel, Operator, UIList

class PAK_UL_TextureList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        if data.enable_multiselect is True:
            layout.prop(item, "is_selected", text = "", icon = "RESTRICT_SELECT_OFF")
        
        if data.enable_bundles is True:
            row = layout.row(align = False)
            row.alignment = 'LEFT'
            row.emboss = 'NORMAL'
            row.enabled = False
            row.separator(factor = 0.05)
            row.label(text = str(len(item.bundle_items)))

            if len(item.bundle_items) > 1:
                row.label(text = "", icon = "RENDERLAYERS")
            else:
                row.label(text = "", icon = "IMAGE_DATA")
            

        name = layout.row(align = False)
        name.alignment = 'EXPAND'
        name.prop(item, "name", text = "", emboss = False)

        export_item = layout.row(align = False)
        export_item.alignment = 'RIGHT'
        export_item.prop(item, "enable_export", text = "")

    def filter_items(self, context, data, property):
        attributes = getattr(data, property)
        flags = []
        indices = [i for i in range(len(attributes))]
        bundles = [item for item in attributes]
        helper_funcs = bpy.types.UI_UL_list

        # Filtering by name
        if self.filter_name:
            flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, bundles, "name", 
                reverse = self.use_filter_sort_reverse)
        if not flags:
            flags = [self.bitflag_filter_item] * len(attributes)

        # Sorting by alphanumerics
        if self.use_filter_sort_alpha:
            indices = helper_funcs.sort_items_by_name(bundles, "name")

        return flags, indices


class PAK_UL_MainMenu(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "PakPal"
    bl_idname = "PROPERTIES_PT_Pak"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):

        layout = self.layout
        addon_prefs = context.preferences.addons[__package__].preferences

        # UI Prompt for when the .blend PakPal data can no longer be found.
        try:
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return

        # //////////////////////////////////
        # LIST MENU
        textures = layout.column(align = True)
        # ui_list_area.label(text = "Hey!")
        textures.template_list("PAK_UL_TextureList", "default", file_data, "bundles", 
                                    file_data, "bundles_list_index", rows = 3, maxrows = 6)

        def ops_checkbox(boolean):
            if boolean:
                return 'CHECKBOX_HLT'
            else:
                return 'CHECKBOX_DEHLT'

        list_options = layout.row(align = True)
        list_options.alignment = 'EXPAND'
        list_options.operator("pak.toggle_multiselect", 
                              icon = ops_checkbox(file_data.enable_multiselect))
        list_options.operator("pak.toggle_bundles", 
                              icon = ops_checkbox(file_data.enable_bundles))
        # list_options.prop(file_data, "enable_multiselect", emboss = True)
        # list_options.prop(file_data, "enable_bundles", emboss = True)


        texture_ops = layout.column(align = True)
        texture_ops.use_property_split = True
        texture_ops.use_property_decorate = False
        # texture_ops.separator()
        texture_ops.operator("pak.refresh_images", icon = 'FILE_REFRESH')
        texture_ops.operator("pak.export_images", icon = 'EXPORT')
        texture_ops.separator()
        texture_ops.operator("wm.url_open", text = "Donate", icon = "FUND").url = "ko-fi.com/takanu"
        # texture_ops.operator("pak.show_preferences", icon = "PREFERENCES")
        texture_ops.separator()

        # //////////////////////////////////
        # SELECTION MENU
        

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


def PAK_UI_CreatePakData(layout):

    # UI Prompt for when the PakPal file data can no longer be found.
    col_export = layout.column(align= True)
    col_export.label(text= "No PakPal data for this .blend file has been found,")
    col_export.label(text= "Please press the button below to generate new data.")
    col_export.separator()
    col_export.separator()
    col_export.operator("pak.create_file_data")
    col_export.separator()
    return

def PAK_UI_CreateSelectionHeader(layout, file_data):
    # Used to create a consistent banner to express what the selected image
    # or bundle is.

    sel_name = 'No Selected Images'
    if file_data.enable_multiselect is True:
        sel_list = [item for item in file_data.bundles if item.is_selected]
        if file_data.enable_bundles:
            sel_name = str(len(sel_list)) + " bundles selected"
        else:
            sel_name = str(len(sel_list)) + " images selected"
    elif len(file_data.bundles) > 0:
        sel_name = file_data.bundles[file_data.bundles_list_index].name
    
    selection_header = layout.row(align = True)
    selection_header_split = selection_header.split(factor = 0.8, align = True)
    selection_header_split.label(text = sel_name, icon = "RESTRICT_SELECT_OFF")
    selection_header.separator()
    