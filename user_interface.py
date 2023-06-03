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

class PAK_UL_BundleStringList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "text", text = "", emboss = False)


class PAK_UL_ExportLocationList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        layout.prop(item, "name", text="", emboss=False)



class PAK_UL_MainMenu(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Pak"
    bl_idname = "PROPERTIES_PT_Pak"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):

        layout = self.layout
        addon_prefs = context.preferences.addons[__package__].preferences

        # UI Prompt for when the .blend Pak data can no longer be found.
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
        list_options.operator("scene.pak_multiselect_toggle", 
                              icon = ops_checkbox(file_data.enable_multiselect))
        list_options.operator("scene.pak_bundles_toggle", 
                              icon = ops_checkbox(file_data.enable_bundles))
        # list_options.prop(file_data, "enable_multiselect", emboss = True)
        # list_options.prop(file_data, "enable_bundles", emboss = True)


        texture_ops = layout.column(align = True)
        texture_ops.use_property_split = True
        texture_ops.use_property_decorate = False
        # texture_ops.separator()
        texture_ops.operator("scene.pak_refresh", icon = 'FILE_REFRESH')
        texture_ops.operator("scene.pak_export", icon = 'EXPORT')
        texture_ops.separator()
        texture_ops.operator("scene.pak_show_preferences", icon = "PREFERENCES")
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

        


class PAK_PT_Location(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Locations"
    bl_parent_id = "PROPERTIES_PT_Pak"

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        try:
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            return

        location_list = layout.row(align= True)
        location_list.template_list("PAK_UL_ExportLocationList", "default", file_data, 
                                   "locations", file_data, "locations_list_index", 
                                   rows = 3, maxrows = 6)
        location_list.separator()

        location_ops = location_list.column(align= True)
        location_ops.operator("scene.pak_addpath", text= "", icon = "ADD")
        location_ops.operator("scene.pak_deletepath", text= "", icon = "REMOVE")

        location_info = layout.column(align = False)
        location_info.use_property_split = True
        location_info.use_property_decorate = False
        location_info.separator()

        count = 0
        for i, item in enumerate(file_data.locations, 1):
            count += 1

        if file_data.locations_list_index > -1 and file_data.locations_list_index < count:
            location_info.prop(file_data.locations[file_data.locations_list_index], "path")
            # location_info.separator()
            location_info.operator_menu_enum("scene.pak_add_export_loc_tag", "path_tags")


def PAK_UI_CreatePakData(layout):

    # UI Prompt for when the Pak file data can no longer be found.
    col_export = layout.column(align= True)
    col_export.label(text= "No Pak data for this .blend file has been found,")
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
        sel_name = str(len(sel_list)) + " images selected"
    elif len(file_data.bundles) > 0:
        sel_name = file_data.bundles[file_data.bundles_list_index].name
    
    selection_header = layout.row(align = True)
    selection_header_split = selection_header.split(factor = 0.8, align = True)
    selection_header_split.label(text = sel_name, icon = "RESTRICT_SELECT_OFF")
    selection_header.separator()
    