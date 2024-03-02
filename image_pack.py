import bpy, os
import numpy as np
from bpy.types import Menu, Panel, Operator
from bpy.props import EnumProperty

from bl_ui.utils import PresetPanel
from bl_operators.presets import AddPresetBase

from .main_menu import PAK_UI_CreateSelectionHeader
from .export_locations import *
from .material_slots import FindMaterialSlotInName
from .image_format_properties import (
    LoadImageFormat, 
    GetImageFileExtension,
    UI_CreateFormatSettings
)

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# PRESET SYSTEM
#
# https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/

# This builds the menu that will be used to display our presets.
#
class PAK_MT_ImagePack_DisplayPresets(Menu): 
    bl_label = 'Image Pack Display Presets' 
    preset_subdir = 'pakpal/image_packs' 
    preset_operator = 'script.execute_preset' 
    draw = Menu.draw_preset

# This operator is for adding and removing presets.
# It tells blender what properties we need fetched.
# 
class PAK_OT_AddImagePackPreset(AddPresetBase, Operator):
    bl_idname = 'pak.add_image_pack_preset'
    bl_label = 'Add Image Pack Preset'
    preset_menu = 'PAK_MT_ImagePack_DisplayPresets'

    # common values used for fetching preset values
    # WARNING: You need to be careful to keep property requests in context here!
    # Otherwise cryptic errors can occur.
    preset_defines = [
        "file_data = bpy.data.objects['>PakPal Blend File Data<'].PAK_FileData",
        "pack_format = file_data.pack_format"
    ]

    # the properties you want to have stored in the preset
    preset_values = [
        'file_data.pack_r_source',
        'file_data.pack_g_source',
        'file_data.pack_b_source',
        'file_data.pack_a_source',

        'file_data.pack_r_channel',
        'file_data.pack_g_channel',
        'file_data.pack_b_channel',
        'file_data.pack_a_channel',

        'file_data.pack_r_invert',
        'file_data.pack_g_invert',
        'file_data.pack_b_invert',
        'file_data.pack_a_invert',

        'file_data.packed_image_suffix',
        
        # MAINTENANCE : This will need to be checked regularly.
        'pack_image_format.file_format', # this goes first as it can replace enums

        'pack_image_format.cineon_black',
        'pack_image_format.cineon_gamma',
        'pack_image_format.cineon_white',

        'pack_image_format.color_management',
        'pack_image_format.color_mode',

        'pack_image_format.compression',

        'pack_image_format.exr_codec',

        'pack_image_format.jpeg2k_codec',
        'pack_image_format.quality',

        'pack_image_format.tiff_codec',
        'pack_image_format.use_cineon_log',

        'pack_image_format.use_jpeg2k_cinema_48',
        'pack_image_format.use_jpeg2k_cinema_preset',
        'pack_image_format.use_jpeg2k_ycc',

        'pack_image_format.use_preview',

        'pack_image_format.color_depth', # this goes last
    ]

    preset_subdir = 'pakpal/image_pack_presets'

class PAK_PT_ImagePack_PresetsOps(PresetPanel, Panel):
    bl_label = "Image Pack Format Presets"
    preset_subdir = "pakpal/image_packs"
    preset_operator = "script.execute_preset"
    preset_add_operator = "pak.add_image_pack_preset"

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# SLOT ADD SYSTEM

class PAK_OT_ImagePack_AddSlotName(Operator):
    """Adds an existing material slot Name to a source slot input"""

    bl_idname = "pak.add_image_pack_slot_name"
    bl_label = "Add Image Source Slot Name"

    def GetSlots(scene, context):
        # identifier, name, (icon (optional)), description, number
        items = [
            ("0", "None",  "", 0),
        ]
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except KeyError:
            return items
        
        strings = addon_prefs.material_slot_names

        for i,x in enumerate(strings):
            items.append((str(i+1), x.text, x.text, i+1))
        return items

    slots: EnumProperty(
        name = "Add Slot Name",
        description = "",
        items = GetSlots,
    )

    path_target: EnumProperty(
        name = "",
        items = (('R', "R", ""),
			    ('G', "G", ""),
			    ('B', "B", ""),
                ('A', "A", ""),
                ('RESULT', "Result", "")),
		description = "",
		default = 'R',
    )

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        # This feels wrong, but I couldn't work out a nicer way D:
        slot_name = self.GetSlots(context)[int(self.slots)][1]
        if self.path_target != 'RESULT':
            slot_name += ", "

        match self.path_target:
            case 'R':
                file_data.pack_r_source += slot_name
            case 'G':
                file_data.pack_g_source += slot_name
            case 'B':
                file_data.pack_b_source += slot_name
            case 'A':
                file_data.pack_a_source += slot_name
            case 'RESULT':
                file_data.packed_image_suffix = slot_name
            case _:
                pass
        return {'FINISHED'}

class PAK_OT_ImagePack_Tutorial(Operator):
    """Open a message describing how material slot Names work"""
    bl_idname = "pak.show_image_pack_tutorial"
    bl_label = ""

    def execute(self, context):

        def tutorial_layout(self, context):
            self.layout.label(text = "Image Packing lets you extract color channels from different")
            self.layout.label(text = "material slots and recombine them into a new image.")
            self.layout.label(text = "")
            self.layout.label(text = "To use this feature you'll need to enable tne Bundles feature.")
            self.layout.label(text = "")
            self.layout.label(text = "To enable Bundles, click on the 'image stack' icon next to")
            self.layout.label(text = "PakPal's image list interface.")

        # Get the current export data
        bpy.context.window_manager.popup_menu(tutorial_layout, title="Material Slot Name Info", icon='HELP')


        return {'FINISHED'}

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# IMAGE PACK MENU


class PAK_PT_ImagePackMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Image Packer"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 4

    def draw_header_preset(self, _context):
        PAK_PT_ImagePack_PresetsOps.draw_panel_header(self.layout)
        self.layout.operator("pak.show_image_pack_tutorial", 
                             text = "", icon = "HELP")

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        try:
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except KeyError:
            return
        
        if file_data.enable_bundles is False:
            warning_label = layout.box()
            warning_label.label(text = "Enable Bundles in the PakPal image list view.", 
                                icon = "ERROR")
            
        pack_test = layout.column(align = False)
        pack_test.use_property_split = True
        pack_test.use_property_decorate = False
        pack_test.active = file_data.enable_bundles
            
        # ////////////////////////////////
        # IMAGE PACK OPERATOR
        has_file_formats = True
        pack_select_box = pack_test.box()
        pack_select_label = pack_select_box.column(align = False)
        pack_select_label.active = file_data.enable_bundles or has_file_formats
        
        PAK_UI_CreateSelectionHeader(pack_select_label, file_data)

        pack_select_options = pack_select_box.column(align = True)
        pack_select_options.use_property_split = True
        pack_select_options.use_property_decorate = False
        pack_select_options.active = file_data.enable_bundles or has_file_formats
        pack_select_options.separator()
        pack_select_options.prop(file_data, "overwrite_image_pack")
        pack_select_options.prop(file_data, "add_fake_user")
        pack_select_options.separator()
        pack_select_options.prop(file_data, "temp_bake_path")
        # bake_menu.separator()
        pack_select_options.separator()
        pack_select_options.separator()

        pack_operator = pack_select_options.column(align = False)
        pack_operator.operator("pak.create_image_pack", icon = "NODE_COMPOSITING")
        pack_test.separator()


        # ////////////////////////////////
        # PACK SLOTS
        pack_slots_box = pack_test.box()
        pack_slots_title = pack_slots_box.column(align = True)
        pack_slots_title.label(text = "Image Packer Sources", icon = "NODE_COMPOSITING")
        pack_test.separator()

        pack_test_r_source = pack_test.row(align = True)
        pack_test_r_source.prop(file_data, "pack_r_source", text = "Red Source")
        pack_test_r_source.operator_menu_enum('pak.add_image_pack_slot_name', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'R'
        
        pack_test_r_channel = pack_test.row(align = False)
        pack_test_r_channel.prop(file_data, "pack_r_channel", expand = True)
        pack_test.prop(file_data, "pack_r_invert", text = "Invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_g_source = pack_test.row(align = True)
        pack_test_g_source.prop(file_data, "pack_g_source", text = "Green Source")
        pack_test_g_source.operator_menu_enum('pak.add_image_pack_slot_name', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'G'
        
        pack_test_g_source = pack_test.row(align = False)
        pack_test_g_source.prop(file_data, "pack_g_channel", expand = True)
        pack_test.prop(file_data, "pack_g_invert", text = "Invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_b_source = pack_test.row(align = True)
        pack_test_b_source.prop(file_data, "pack_b_source", text = "Blue Source")
        pack_test_b_source.operator_menu_enum('pak.add_image_pack_slot_name', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'B'
        
        pack_test_b_source = pack_test.row(align = False)
        pack_test_b_source.prop(file_data, "pack_b_channel", expand = True)
        pack_test.prop(file_data, "pack_b_invert", text = "Invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_a_source = pack_test.row(align = True)
        pack_test_a_source.prop(file_data, "pack_a_source", text = "Alpha Source")
        pack_test_a_source.operator_menu_enum('pak.add_image_pack_slot_name', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'A'
        
        pack_test_a_source = pack_test.row(align = False)
        pack_test_a_source.prop(file_data, "pack_a_channel", expand = True)
        pack_test.prop(file_data, "pack_a_invert", text = "Invert")
        pack_test.separator()
        pack_test.separator()
        
        pack_test_result = pack_test.row(align = True)
        pack_test_result.prop(file_data, "packed_image_suffix")
        pack_test_result.operator_menu_enum('pak.add_image_pack_slot_name', "slots",
                                             text = "",
                                             icon = "TRIA_DOWN").path_target = 'RESULT'

        # ////////////////////////////////
        # PACK FORMATS
        pack_test.separator()
        
        try:
            pack_format_box = pack_test.box()
            pack_format = pack_format_box.column(align = True)
            pack_format.label(text = "Image Format Settings", icon = "FILE_IMAGE")

            pack_format_options = pack_test.column(align = False)
            pack_format_options.use_property_split = True
            pack_format_options.use_property_decorate = False
            pack_format_options.separator()
            # TODO: Add color management
            pack_format = file_data.pack_format
            UI_CreateFormatSettings(pack_format_options, pack_format)
            pack_format_options.separator()
            pack_format_options.separator()

        except:
            has_file_formats = False
            UI_CreateFormatSettings(pack_test)
            pack_test.separator()
            pack_test.separator()
        
        

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# IMAGE PACK OPERATOR


class PAK_OT_CreateImagePack(Operator):
    """Creates a new packed image based on channels from existing images found within a bundle.

    NOTE - You'll need to select at least one bundle from the PakPal image list in order to create a packed image"""

    bl_idname = "pak.create_image_pack"
    bl_label = "Create Image Pack From Selection"

    # Thanks!
    # https://blender.stackexchange.com/questions/19500/controling-compositor-by-python
    # https://docs.blender.org/api/current/bpy.types.CompositorNode.html
    def create_compositor_packer(self):
        
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # BUILD IMAGES
        # NOTE: Image color output includes the alpha channel
        r_image_node = tree.nodes.new(type = 'CompositorNodeImage')
        r_image_node.image = self.source_r
        r_image_node.location = 0,0

        g_image_node = tree.nodes.new(type = 'CompositorNodeImage')
        g_image_node.image = self.source_g
        g_image_node.location = 0,-350

        b_image_node = tree.nodes.new(type = 'CompositorNodeImage')
        b_image_node.image = self.source_b
        b_image_node.location = 0,-700

        a_image_node = tree.nodes.new(type = 'CompositorNodeImage')
        a_image_node.image = self.source_a
        a_image_node.location = 0,-1050

        # BUILD INVERTS
        # TODO : Check back later when a useful copy function becomes available.
        r_invert = tree.nodes.new(type = 'CompositorNodeInvert')
        r_invert.location = 250,0
        r_invert.invert_alpha = True
        r_invert_fac = r_invert.inputs['Fac']
        r_invert_fac.default_value = self.invert_r

        g_invert = tree.nodes.new(type = 'CompositorNodeInvert')
        g_invert.location = 250,-350
        g_invert.invert_alpha = True
        g_invert_fac = g_invert.inputs['Fac']
        g_invert_fac.default_value = self.invert_g

        b_invert = tree.nodes.new(type = 'CompositorNodeInvert')
        b_invert.location = 250,-700
        b_invert.invert_alpha = True
        b_invert_fac = b_invert.inputs['Fac']
        b_invert_fac.default_value = self.invert_b

        a_invert = tree.nodes.new(type = 'CompositorNodeInvert')
        a_invert.location = 250,-1050
        a_invert.invert_alpha = True
        a_invert_fac = a_invert.inputs['Fac']
        a_invert_fac.default_value = self.invert_a

        links.new(r_image_node.outputs[0], r_invert.inputs[1])
        links.new(g_image_node.outputs[0], g_invert.inputs[1])
        links.new(b_image_node.outputs[0], b_invert.inputs[1])
        links.new(a_image_node.outputs[0], a_invert.inputs[1])

        # BUILD SEPARATORS
        r_separate = tree.nodes.new(type = 'CompositorNodeSeparateColor')
        r_separate.mode = 'RGB'
        r_separate.location = 500,0
        g_separate = tree.nodes.new(type = 'CompositorNodeSeparateColor')
        g_separate.mode = 'RGB'
        g_separate.location = 500,-350
        b_separate = tree.nodes.new(type = 'CompositorNodeSeparateColor')
        b_separate.mode = 'RGB'
        b_separate.location = 500,-700
        a_separate = tree.nodes.new(type = 'CompositorNodeSeparateColor')
        a_separate.mode = 'RGB'
        a_separate.location = 500,-1050

        links.new(r_invert.outputs[0], r_separate.inputs[0])
        links.new(g_invert.outputs[0], g_separate.inputs[0])
        links.new(b_invert.outputs[0], b_separate.inputs[0])
        links.new(a_invert.outputs[0], a_separate.inputs[0])
        
        # BUILD COMBINE
        def make_separate_link(separate_node, target_output, combine_node, target_input):
            color_slot = {'R': 0, 'G': 1, 'B':2, 'A':3}
            color_input = color_slot[target_output]
            color_output = color_slot[target_input]
            links.new(separate_node.outputs[color_input], combine_node.inputs[color_output])

        combine_color = tree.nodes.new(type = 'CompositorNodeCombineColor')
        combine_color.location = 750,-550
        combine_color.update()

        if self.source_r is not None:
            make_separate_link(r_separate, self.channel_r, combine_color, 'R')
        if self.source_g is not None:
            make_separate_link(g_separate, self.channel_g, combine_color, 'G')
        if self.source_b is not None:
            make_separate_link(b_separate, self.channel_b, combine_color, 'B')
        if self.source_a is not None:
            make_separate_link(a_separate, self.channel_a, combine_color, 'A')

        # ADD OUTPUT
        output_node = tree.nodes.new(type = 'CompositorNodeViewer')
        output_node.location = 1000, -550

        # output_node = tree.nodes.new(type = 'CompositorNodeOutputFile')
        # output_node.location = 1000, -550
        # output_node.base_path = self.file_directory
        # output_node.file_slots[0].path = self.file_name + ".png"
        # output_node.file_slots[0].save_as_render = False
        
        links.new(combine_color.outputs[0], output_node.inputs[0])

        # This renders whatever is on the compositor.
        # When using a File Output node it will forcefully add a frame number to the end.
        bpy.ops.render.render(animation=False, write_still=False, use_viewport=False, layer="", scene="")

    
    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}
        
        def get_image_for_slot(bundle, source_slots):
            if source_slots == "":
                return None
            
            source_slots = source_slots.replace(",", "")
            source_slot_strings = source_slots.split()
            source_slot_strings = [s for s in source_slot_strings]

            for bundle_item in bundle.pak_items:
                filename = os.path.splitext(bundle_item.tex.name)[0]
                match = FindMaterialSlotInName(addon_prefs, filename, source_slot_strings,
                                               file_data.case_sensitive_matching)

                if match:
                    return bundle_item.tex
            
            return None
        
        if file_data.enable_bundles is False:
            self.report({'WARNING'}, "Image packing requires Bundles to be enabled.")
            return {'FINISHED'}
        
        # /////////////////////////////////////////////////////////////////
        # BUILD SCENE
        
        # NOTE - The context won't actually change unless we escape the properties context.
        # Properties > Output has it's own scene context!
        # TODO: Potentially find a way to change the scene context for just the properties panel.
        old_type = context.area.type
        context.area.type = 'VIEW_3D'
        bpy.ops.scene.new(type = 'NEW')
        composite_scene = bpy.context.scene

        
        # /////////////////////////////////////////////////////////////////
        # TRANSFER IMAGE FORMAT SETTINGS
        # try:
        pack_format = file_data.pack_format
        composite_format = composite_scene.render.image_settings
        LoadImageFormat(pack_format, composite_format)

        # except:
        #     bpy.data.scenes.remove(composite_scene, do_unlink = True)
        #     context.area.type = old_type

        #     self.report({'WARNING'}, "Something went wrong with Image Format Settings, check that all properties have been set")
        #     return {'FINISHED'}
        
        # Set the composite scene to ensure colors aren't edited
        # It's easier to set it in the fake scene :D
        composite_scene.render.image_settings.color_management = 'OVERRIDE'
        composite_scene.view_settings.view_transform = 'Standard'
        composite_scene.view_settings.look = 'None'

        report_info = {'new_images': 0, 'updated_images': 0, 'not_found': 0, 'not_overwritten': 0}
        valid_bundles = [file_data.bundles[file_data.bundles_list_index]]
        if file_data.enable_multiselect:
            valid_bundles = [b for b in file_data.bundles 
                            if b.is_selected or file_data.enable_multiselect is False]
        
        
        for bundle in valid_bundles:
            
            # ///////////////////////////////////////////////////////////////////////////
            # PREPARE PROPERTIES

            file_ext = GetImageFileExtension(pack_format.file_format)

            file_name = bundle.name + file_data.packed_image_suffix
            file_directory = CreateFilePath(file_data.temp_bake_path)
            file_path = file_directory + file_name + file_ext

            # Skip if we aren't allowed to overwrite an image.
            if file_name in bpy.data.images and file_data.overwrite_image_pack is False:
                report_info['not_overwritten'] += 1
                continue

            # Access source, channel and inversion data
            self.source_r = get_image_for_slot(bundle, file_data.pack_r_source)
            self.source_g = get_image_for_slot(bundle, file_data.pack_g_source)
            self.source_b = get_image_for_slot(bundle, file_data.pack_b_source)
            self.source_a = get_image_for_slot(bundle, file_data.pack_a_source)

            if (self.source_r and self.source_g 
                and self.source_b and self.source_a is None):
                report_info['not_found'] += 1
                continue

            self.channel_r = file_data.pack_r_channel
            self.channel_g = file_data.pack_g_channel
            self.channel_b = file_data.pack_b_channel
            self.channel_a = file_data.pack_a_channel

            self.invert_r = file_data.pack_r_invert
            self.invert_g = file_data.pack_g_invert
            self.invert_b = file_data.pack_b_invert
            self.invert_a = file_data.pack_a_invert

            # ///////////////////////////////////////////////////////////////////////////
            # COMPOSITE AND RENDER
            
            self.create_compositor_packer()

            # Store the output image in it's own buffer and datablock.
            viewer = bpy.data.images['Viewer Node']

            # use save_render to avoid the viewer node datablock from becoming a FILE type.
            viewer.save_render(filepath = file_path)

            # ///////////////////////////////////////////////////////////////////////////
            # LOAD NEW IMAGE

            new_image = None
            
            if file_name in bpy.data.images:
                new_image = bpy.data.images[file_name]
                new_image.unpack(method = 'REMOVE')
                new_image.filepath = file_path
                new_image.name = file_name
                new_image.reload()

                report_info['updated_images'] += 1
            else:
                new_image = bpy.data.images.load(file_path, check_existing = True)
                new_image.filepath = file_path
                new_image.name = file_name

                bundle_proxy = bundle.pak_items[0].tex.PAK_Img

                # add the new image to the bundle!
                new_bundle_item = bundle.pak_items.add()
                new_bundle_item.tex = new_image
                new_bundle_item.tex.PAK_Img.enable_export = bundle_proxy.enable_export
                new_bundle_item.tex.PAK_Img.export_location = bundle_proxy.export_location

                report_info['new_images'] += 1

            new_image.pack()
            new_image.use_fake_user = file_data.add_fake_user

        # TODO: Delete the saved image once it's been packed. (decided not to right now just in case)
        # TODO: Fully test info statements

        # ///////////////////////////////////////////////////////////////////////////
        # RESTORE SCENE
        # Delete the composite scene and change the area context back.
        bpy.data.scenes.remove(composite_scene, do_unlink = True)
        context.area.type = old_type

        info = ""
        new_image_info = ""
        updated_image_info = ""
        failed_image_info = ""
        not_overwritten_image_info = ""

        print(report_info)

        if report_info['new_images'] == 1:
            new_image_info = str(report_info['new_images']) + " new image"
        elif report_info['new_images'] > 1:
            new_image_info = str(report_info['new_images']) + " new images"

        if report_info['updated_images'] == 1:
            updated_image_info += str(report_info['updated_images']) + " image"
        elif report_info['updated_images'] > 1:
            updated_image_info += str(report_info['updated_images']) + " images"

        if report_info['not_found'] == 1:
            failed_image_info += str(report_info['not_found']) + " bundle"
        elif report_info['not_found'] > 1:
            failed_image_info += str(report_info['not_found']) + " bundles"
        
        if report_info['not_overwritten'] == 1:
            not_overwritten_image_info += str(report_info['not_overwritten']) + " image"
        elif report_info['not_overwritten'] > 1:
            not_overwritten_image_info += str(report_info['not_overwritten']) + " images"
        
        if (new_image_info == "" and updated_image_info == "" and 
             failed_image_info == "" and not_overwritten_image_info == ""):
            info = "PakPal couldn't find material slots to pack any selected bundle."
            self.report({'WARNING'}, info)

        else:
            if new_image_info != "":
                if failed_image_info == "":
                    info = "PakPal packed " + new_image_info + ".  "
                else:
                    info = "PakPal packed " + new_image_info + " and updated " + updated_image_info + ".  "
            elif updated_image_info != "":
                info = "PakPal updated " + updated_image_info + ".  "
            
            if not_overwritten_image_info != "":
                info += not_overwritten_image_info + " were not overwritten.  "
            
            if failed_image_info != "":
                info += "material slots for " + failed_image_info + " couldn't be found."

            self.report({'INFO'}, info)
        

        return {'FINISHED'}


