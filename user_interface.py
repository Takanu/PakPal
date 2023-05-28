import bpy
from bpy.types import Menu, Panel, Operator, UIList

class PAK_UL_TextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        # if file_data.enable_multiselect is True:
        #     layout.prop(item, "is_selected", text="", emboss=False)

        layout.prop(item.tex, "name", text="", emboss=False)
        layout.prop(item.tex.PAK_Tex, "enable_export", text="")


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
            PAK_CreatePakDataUI(layout)
            return

        # //////////////////////////////////
        # LIST MENU
        textures = layout.column(align = True)
        # ui_list_area.label(text = "Hey!")
        textures.template_list("PAK_UL_TextureList", "default", file_data, "textures", 
                                    file_data, "textures_list_index", rows = 3, maxrows = 6)
        textures.separator()
        textures.operator("scene.pak_refresh", icon = 'FILE_REFRESH')
        textures.separator()
        textures.operator("scene.pak_export", icon = 'EXPORT')
        textures.separator()

        # //////////////////////////////////
        # SELECTION MENU
        selection = layout.column(align = True)
        selection.use_property_split = True
        selection.use_property_decorate = False

        if len(file_data.textures) > 0:
            entry = file_data.textures[file_data.textures_list_index]
            tex = entry.tex.PAK_Tex
            selection.prop(tex, "enable_export")
            selection.separator()
            selection.prop(tex, "export_location")
            selection.separator()
        
        

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


def PAK_CreatePakDataUI(layout):

    # UI Prompt for when the Pak file data can no longer be found.
    col_export = layout.column(align= True)
    col_export.label(text= "No Pak data for this .blend file has been found,")
    col_export.label(text= "Please press the button below to generate new data.")
    col_export.separator()
    col_export.separator()
    col_export.operator("pak.create_file_data")
    col_export.separator()
    return
