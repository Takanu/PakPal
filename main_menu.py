import bpy

class PAK_UL_TextureList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        if data.enable_bundles is True:
            row = layout.row(align = False)
            row.alignment = 'LEFT'
            row.emboss = 'NORMAL'
            row.enabled = False
            row.separator(factor = 0.05)
            row.label(text = str(len(item.pak_items)))

            if len(item.pak_items) > 1:
                row.label(text = "", icon = "RENDERLAYERS")
            else:
                row.label(text = "", icon = "IMAGE_DATA")
            

        name = layout.row(align = False)
        name.alignment = 'EXPAND'
        name.prop(item, "name", text = "", emboss = False)
        

        # EXTRA INFO
        # //////////////
        if data.enable_bundles is False:

            # FORMAT TYPE
            if data.show_file_format is True:
                format_type = str(item.pak_items[0].tex.file_format)
                user_box = layout.box()
                user_box.alignment = 'RIGHT'
                user_box.scale_y = 0.5
                user_box.label(text = format_type + " ")

            # MATERIAL COUNT
            if data.show_material_count is True:
                material_count = len([m for m in bpy.data.materials if m.user_of_id(item.pak_items[0].tex)])
                mat_box = layout.box()
                mat_box.alignment = 'RIGHT'
                mat_box.scale_y = 0.5
                mat_box.label(text = str(material_count), icon = 'MATERIAL')

            # USER COUNT
            if data.show_user_count is True:
                user_count = str(item.pak_items[0].tex.users)
                user_box = layout.box()
                user_box.alignment = 'RIGHT'
                user_box.scale_y = 0.5
                user_box.label(text = user_count, icon = 'USER')

            # FAKE USER
            if data.show_fake_user is True:
                fake_box = layout.box()
                fake_box.alignment = 'RIGHT'
                fake_box.scale_y = 0.5
                if item.pak_items[0].tex.use_fake_user is True:
                    fake_box.label(text = '', icon = 'FAKE_USER_ON')
                else:
                    fake_box.label(text = '', icon = 'FAKE_USER_OFF')
        
        # ENABLE EXPORT
        # //////////////
        export_item = layout.row(align = False)
        export_item.alignment = 'RIGHT'
        
        export_icon = "RESTRICT_RENDER_ON"
        if item.enable_export == True:
            export_icon = "RESTRICT_RENDER_OFF"

        export_item.prop(item, "enable_export", text = "", icon = export_icon, emboss = False)

        # MULTISELECT
        if data.enable_multiselect is True:
            select_icon = "RESTRICT_SELECT_ON"
            if item.is_selected == True:
                select_icon = "RESTRICT_SELECT_OFF"
            layout.prop(item, "is_selected", text = "", icon = select_icon, emboss = False)

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

class PAK_PT_TextureListOptions(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Image List Options"
    bl_idname = "PROPERTIES_PT_pak_texture_options"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'HEADER'

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData

        options = layout.column(align = True)
        options.label(text = "Display Options")
        options.separator()

        display_options = options.column(align = True)
        display_options.prop(file_data, 'show_file_format')
        display_options.prop(file_data, 'show_material_count')
        display_options.prop(file_data, 'show_user_count')
        display_options.prop(file_data, 'show_fake_user')
        display_options.separator()
        display_options.separator()
        display_options.prop(file_data, 'show_hidden')
        display_options.separator()



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
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return

        # //////////////////////////////////
        # LIST MENU
        texture_list_area = layout.row(align = False)
        texture_list_ui = texture_list_area.column(align = True)
        texture_list_ui.template_list("PAK_UL_TextureList", "default", file_data, "bundles", 
                                    file_data, "bundles_list_index", rows = 7, maxrows = 12)
        texture_list_ui.separator()

        def ops_checkbox(boolean):
            if boolean:
                return 'CHECKBOX_HLT'
            else:
                return 'CHECKBOX_DEHLT'
        
        def ops_img(boolean):
            if boolean:
                return 'RENDERLAYERS'
            else:
                return 'IMAGE_DATA'
            
        # TODO: Try making this look like an expanded enum?

        list_options = texture_list_area.column(align = True)

        list_options.operator("pak.toggle_multiselect", 
                              icon = 'RESTRICT_SELECT_OFF',
                              text = "",
                              depress = file_data.enable_multiselect)

        list_options.operator("pak.toggle_bundles", 
                              icon = 'RENDERLAYERS',
                              text = "",
                              depress = file_data.enable_bundles)
        list_options.separator()
        
        list_options.operator("pak.refresh_images", 
                              icon = 'FILE_REFRESH',
                              text = "")
        list_options.separator()

        list_options.operator("image.open", 
                              icon = 'FILEBROWSER',
                              text = "")
        
        list_options.operator("pak.delete_selected_images", 
                              icon = "TRASH",
                              text = "")
        list_options.separator()
        
        list_options.popover(panel = "PROPERTIES_PT_pak_texture_options",
                             icon = 'DOWNARROW_HLT',
                             text = "")
        
        
                              

        # //////////////////////////////////
        # SELECTION MENU
        preview_area = layout.row(align = False)
        preview_area_image = preview_area.column(align = True)
        

        # The template preview cannot be allowed to try and preview data that doesn't exist,
        # otherwise it will crash
        has_preview = False
        if len(file_data.bundles) > 0 and file_data.preview_tex is not None:
            if file_data.preview_tex.image is not None:
                has_preview = True
        
        if has_preview:
            preview_img = file_data.preview_tex.image
            preview_area_image.template_preview(file_data.preview_tex)

            # BUG: If you contain a texture preview in a box, the preview becomes darker.  Report to Blender?
            preview_area_info = preview_area_image.box()
            preview_area_info.alignment = 'EXPAND'
            preview_area_info.label(text = preview_img.name, 
                                    icon = "HIDE_OFF")
            # print(preview_img)
            image_info = str(preview_img.size[0])
            image_info += " x "
            image_info += str(preview_img.size[1]) + ", "
            image_info += str(preview_img.file_format)

            # TODO - Add additional image details
            # image_info += str(preview_img.depth)
            preview_area_info.label(text = image_info)
            
        else:
            preview_area_info = preview_area_image.box()
            preview_area_info.label(text = "No images available",
                                    icon = "HIDE_OFF")

        preview_area_options = preview_area.column(align = True)
        preview_area_options.alignment = 'RIGHT'
        preview_area_options.prop(file_data, 'preview_rgb')
        
        # //////////////////////////////////
        # DONATE
        preview_area_buffer = layout.column()
        donate = layout.row(align = True)
        donate.operator("wm.url_open", text = "Donate", icon = "FUND").url = "ko-fi.com/takanu"
        donate.separator()
        donate.separator()
        donate.separator()
        donate.separator()
        donate.separator()



def PAK_UI_CreatePakData(layout):

    # UI Prompt for when the PakPal file data can no longer be found.
    col_export = layout.column(align = True)
    col_export.label(text= "No PakPal data for this .blend file has been found,")
    col_export.label(text= "Please press the button below to generate new data.")
    col_export.separator()

    col_box_1 = layout.box()
    col_box_1_contents = col_box_1.column(align = True)
    col_box_1_contents.label(text = "PakPal creates two sets of information visible in the file.",
                             icon = "INFO")
    col_box_1_contents.label(text = "")
    col_box_1_contents.label(text = "The first is an empty object that stores file data such as",
                             icon = "RADIOBUT_ON")
    col_box_1_contents.label(text = "         export locations and image pack settings.")
    col_box_1_contents.label(text = "")
    col_box_1_contents.label(text = "The second is two Compositor Output nodes, used to store",
                             icon = "RADIOBUT_ON")
    col_box_1_contents.label(text = "         Image Format information for exports and image packing.")
    col_box_1_contents.label(text = "")
    col_box_1_contents.label(text = "This is due to limitations with Blender's Python API,",
                             icon = "ERROR")
    col_box_1_contents.label(text = "        please don't delete them while using PakPal!")

    col_export.separator()
    col_export.operator("pak.create_file_data")
    col_export.separator()
    return

def PAK_UI_CreateSelectionHeader(layout, file_data):
    # Used to create a consistent banner to express what the selected image
    # or bundle is.

    header_text = "Selection - "

    sel_name = 'No Selected Images'
    sel_list = []
    if file_data.enable_multiselect is True:
        sel_list = [item for item in file_data.bundles if item.is_selected]
        
        if file_data.enable_bundles:
            if len(sel_list) > 1 or len(sel_list) == 0:
                sel_name = str(len(sel_list)) + " bundles"
            else:
                sel_name = str(len(sel_list)) + " bundle"

        else:
            if len(sel_list) > 1 or len(sel_list) == 0:
                sel_name = str(len(sel_list)) + " images"
            else:
                sel_name = str(len(sel_list)) + " image"

    elif len(file_data.bundles) > 0:
        sel_name = file_data.bundles[file_data.bundles_list_index].name

        if file_data.enable_bundles:
            bundle = file_data.bundles[file_data.bundles_list_index]

            sel_name += "  (" + str(len(bundle.pak_items)) + ")"
    
    selection_header = layout.column(align = True)
    selection_header.label(text = header_text + sel_name, icon = "RESTRICT_SELECT_OFF")

    # Added this so operators have a quick way to check whether or not the selection conditions are valid
    return {"selection_count": len(sel_list), "is_bundle": file_data.enable_bundles}
    
def CreatePakPreviewTexture():

    try:
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except:
        print('No PakPal file data found, cannot create preview texture.')
        return

    if 'PakPal Preview' in bpy.data.textures: 
        bpy.data.batch_remove(bpy.data.textures['PakPal Preview'])

    file_data.preview_tex = None

    file_data.preview_tex = bpy.data.textures.new(name = "PakPal Preview", type = 'IMAGE')
    tex = file_data.preview_tex

    tex.intensity = 1.0
    tex.contrast = 1.0
    tex.saturation = 1.0

    tex.factor_red = 1.0
    tex.factor_green = 1.0
    tex.factor_blue = 1.0

    tex.use_color_ramp = False
