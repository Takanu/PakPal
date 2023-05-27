import bpy
from bpy.types import Menu, Panel, Operator, UIList


class PAK_UL_MainMenu(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Pak"
    bl_idname = "PROPERTIES_PT_Pak"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):

        layout = self.layout
        scene_data = context.scene.PAK_SceneData
        addon_prefs = context.preferences.addons[__package__].preferences

        # UI Prompt for when the .blend Pak data can no longer be found.
        try:
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            PAK_CreatePakDataUI(layout)
            return

        # //////////////////////////////////
        # LIST MENU
        tex_list = layout.column(align=True)
        # ui_list_area.label(text = "Hey!")
        tex_list.template_list("PAK_UL_TextureList", "default", scene_data, "tex_list", 
                                    scene_data, "selected_list_index", rows=3, maxrows=6)
        tex_list.separator()
        tex_list.operator("scene.pak_refresh")
        # ui_list_column.operator("scene.satl_render_all")

        # ui_list_column.separator()
        # ui_list_area.separator()

        # ui_list_column = ui_list_area.column(align=True)
        # ui_list_column.operator("scene.satl_add", text="", icon="ADD")
        # ui_list_column.operator("scene.satl_remove", text="", icon="REMOVE")
        # ui_list_column.separator()
        # ui_list_column.operator("scene.satl_ui_shiftup", text="", icon="TRIA_UP")
        # ui_list_column.operator("scene.satl_ui_shiftdown", text="", icon="TRIA_DOWN")
        # ui_list_column.separator()
        # ui_list_column.operator("scene.satl_ui_duplicate", text="", icon="DUPLICATE")
        # ui_list_column.separator()

        
    

        # # //////////////////////////////////
        # # PRESET OPTIONS
        # render_options_area = layout.column(align=False)

        # count = 0
        # for i, item in enumerate(sat_data.sat_presets, 1):
        #     count += 1
        
        # list_index = sat_data.sat_selected_list_index

        # if list_index > -1 and list_index < count:
        #     render_selected = sat_data.sat_presets[list_index]
        #     render_output = render_options_area.column(align=True)
        #     render_output.use_property_split = True
        #     render_output.use_property_decorate = False
        #     render_output.separator()

        #     # render_options_list.prop(render_selected, "name")
        #     render_output.prop(render_selected, "output_dir")
        #     render_output.prop(render_selected, "output_name")
        #     render_output.separator()
        #     render_output.separator()
        #     render_output.separator()

        #     render_format_selector = render_options_area.row(align=True)
        #     render_format_selector_split = render_format_selector.split(factor=0.4, align=True)
        #     render_format_selector_split.label(text="Render Type", icon="RENDER_RESULT")
        #     render_format_selector_split.prop(render_selected, "render_type", text="")
        #     render_options_area.separator()
            
        #     render_format_box = render_options_area.box()
        #     render_format_area = render_format_box.column(align=True)
        #     render_format_area.separator()


        #     if render_selected.render_type == 'Skybox':
        #         render_format = render_selected.data_skybox

        #         # First we have to splice the space up weirdly to get padding on each side
        #         render_tab_area = render_format_area.row(align=True)
        #         render_tab_area.separator()

        #         render_format_options = render_tab_area.column(align=True)
        #         render_format_options.use_property_split = True
        #         render_format_options.use_property_decorate = False

        #         # Scene Settings
        #         render_format_options.prop(render_format, "world_material")
        #         render_format_options.prop(render_format, "view_layer")
        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()
                
        #         # Render Engine Settings
        #         render_format_options.prop(render_format, "render_engine")
        #         render_format_options.separator()
        #         render_format_options.prop(render_format, "resolution")
        #         render_format_options.prop(render_format, "samples")
        #         render_format_options.separator()

        #         if render_format.render_engine == 'Cycles':
        #             # This is used to ensure the boolean label is aligned.
        #             render_format_list_denoiser = render_format_options.column(align=True, 
        #                 heading="Use Denoiser")
        #             render_format_list_denoiser.prop(render_format, "cycles_use_denoiser", text="")

        #         elif render_format.render_engine == 'Eevee':
        #             # This is used to ensure the boolean label is aligned.
        #             render_format_list_denoiser = render_format_options.column(align=True, 
        #                 heading="Disable Post-Processing")
        #             render_format_list_denoiser.prop(render_format, "eevee_disable_pp", text="")
                
        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_col_mode = render_format_options.row(align=True)
        #         render_format_col_mode.prop(render_format, "color_mode", expand=True)

        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()
                

        #         # Color Settings
        #         render_format_options.prop(render_selected, "color_view_transform")
        #         render_format_options.prop(render_selected, "color_look")
        #         render_format_options.separator()
        #         render_format_options.prop(render_selected, "color_exposure")
        #         render_format_options.prop(render_selected, "color_gamma")

        #         render_format_options.separator()
        #         render_format_options.separator()

            


        #     if render_selected.render_type == 'Direct Camera':
        #         render_format = render_selected.data_camera

        #         # First we have to splice the space up weirdly to get padding on each side
        #         render_tab_area = render_format_area.row(align=True)
        #         render_tab_area.separator()

        #         # In order to get our tabs we have to use property split later
        #         render_format_options = render_tab_area.column(align=True)
        #         render_format_options.use_property_split = True
        #         render_format_options.use_property_decorate = False

        #         # Scene Settings
        #         render_format_options.prop(render_format, "target_camera")
        #         render_format_options.prop(render_format, "view_layer")
        #         render_format_options.separator()
        #         render_format_options.prop(render_format, "world_material")
        #         render_format_options.prop(render_format, "replacement_material")
        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()


        #         # Render Engine Settings
        #         render_format_options.prop(render_format, "render_engine")
        #         render_format_options.separator()
        #         render_format_options.prop(render_format, "resolution_x")
        #         render_format_options.prop(render_format, "resolution_y")
        #         render_format_options.prop(render_format, "samples")
        #         render_format_options.separator()
                

        #         if render_format.render_engine == 'Cycles':
        #             # This is used to ensure the boolean label is aligned.
        #             render_format_list_denoiser = render_format_options.column(align=True, 
        #                 heading="Use Denoiser")
        #             render_format_list_denoiser.prop(render_format, "cycles_use_denoiser", text="")
                
        #         elif render_format.render_engine == 'Eevee':
        #             # This is used to ensure the boolean label is aligned.
        #             render_format_list_denoiser = render_format_options.column(align=True, 
        #                 heading="Disable Post-Processing")
        #             render_format_list_denoiser.prop(render_format, "eevee_disable_pp", text="")
                
        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()


        #         # Export Format Settings
        #         render_format_options.prop(render_format, "file_format")
        #         render_format_options.separator()

        #         file_format = render_format.file_format

        #         if file_format in ['JPEG', 'CINEON', 'HDR']:
        #             render_format_col_mode = render_format_options.row(align=True)
        #             render_format_col_mode.prop(render_format, "color_mode_bw", expand=True)
                
        #         else:
        #             render_format_col_mode = render_format_options.row(align=True)
        #             render_format_col_mode.prop(render_format, "color_mode", expand=True)

        #         if file_format in ['PNG']:
        #             render_format_col_depth = render_format_options.row(align=True)
        #             render_format_col_depth.prop(render_format, "color_depth", expand=True)
                
        #         if file_format in ['PNG']:
        #             render_format_options.prop(render_format, "compression")
                
        #         if file_format in ['JPEG']:
        #             render_format_options.prop(render_format, "quality")

        #         render_format_options.separator()
        #         render_format_options.separator()
        #         render_format_options.separator()

        #         # Color Settings
        #         render_format_options.prop(render_selected, "color_view_transform")
        #         render_format_options.prop(render_selected, "color_look")
        #         render_format_options.separator()
        #         render_format_options.prop(render_selected, "color_exposure")
        #         render_format_options.prop(render_selected, "color_gamma")

        #         render_format_options.separator()
        #         render_format_options.separator()

        #     # Adds the padding on the right side.
        #     render_tab_area.separator()

class PAK_PT_Location(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Locations"
    bl_parent_id = "PROPERTIES_PT_Pak"

    # @classmethod
    # def poll(cls, context):
    #     preferences = context.preferences
    #     addon_prefs = preferences.addons[__package__].preferences

    #     try:
    #         cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
    #     except KeyError:
    #         return False
    #     return True

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        scene_data = context.scene.PAK_SceneData

        # col_location = layout.row(align= True)
        # col_location.template_list("CAPSULE_UL_Path_Default", "default", cap_file, "location_presets", cap_file, "location_presets_listindex", rows=3, maxrows=6)

        # col_location.separator()

        # row_location = col_location.column(align= True)
        # row_location.operator("scene.cap_addpath", text= "", icon = "ADD")
        # row_location.operator("scene.cap_deletepath", text= "", icon = "REMOVE")

        # location_options = layout.column(align= False)
        # location_options.use_property_split = True
        # location_options.use_property_decorate = False
        # location_options.separator()

        # count = 0
        # for i, item in enumerate(cap_file.location_presets, 1):
        #     count += 1

        # if cap_file.location_presets_listindex > -1 and cap_file.location_presets_listindex < count:
        #     location_options.prop(cap_file.location_presets[cap_file.location_presets_listindex], "path")
        #     location_options.operator_menu_enum("scene.cap_add_file_location_tag", "path_tags")


def PAK_CreatePakDataUI(layout):

    # UI Prompt for when the .blend Capsule data can no longer be found.
    col_export = layout.column(align= True)
    col_export.label(text= "No Pak data for this .blend file has been found,")
    col_export.label(text= "Please press the button below to generate new data.")
    col_export.separator()
    col_export.separator()
    col_export.operator("pak.create_file_data")
    col_export.separator()
    return
