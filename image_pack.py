import bpy, os
import numpy as np
from bpy.types import Menu, Panel, Operator
from bpy.props import EnumProperty

from bl_ui.utils import PresetPanel
from bl_operators.presets import AddPresetBase

from .user_interface import PAK_UI_CreateSelectionHeader

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# PRESET SYSTEM
#
# https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/

# This builds the menu that will be used to display our presets.
#
class PAK_MT_ImagePack_DisplayPresets(Menu): 
    bl_label = 'Image Pack Display Presets' 
    preset_subdir = 'pak/image_packs' 
    preset_operator = 'script.execute_preset' 
    draw = Menu.draw_preset

# This operator is for adding and removing presets.
# It tells blender what properties we need fetched.
# 
class PAK_OT_AddImagePackPreset(AddPresetBase, Operator):
    bl_idname = 'scene.pak_add_image_pack_preset'
    bl_label = 'Add Image Pack Preset'
    preset_menu = 'PAK_MT_ImagePack_DisplayPresets'

    # common values used for fetching preset values
    # WARNING: You need to be careful to keep property requests in context here!
    preset_defines = [
        "addon_prefs = bpy.context.preferences.addons['Pak'].preferences",
        "file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData",
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
    ]

    preset_subdir = 'pak/image_packs'

class PAK_PT_ImagePack_PresetsOps(PresetPanel, Panel):
    bl_label = "Image Pack Format Presets"
    preset_subdir = "pak/image_packs"
    preset_operator = "script.execute_preset"
    preset_add_operator = "scene.pak_add_image_pack_preset"

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# SLOT ADD SYSTEM

class PAK_OT_ImagePack_AddSlotName(Operator):
    """Adds an existing Bundle String to a source slot input"""

    bl_idname = "scene.pak_imagepack_addslotname"
    bl_label = "Add Image Source Slot Name"

    def GetSlots(scene, context):
        # identifier, name, (icon (optional)), description, number
        items = [
            ("0", "None",  "", 0),
        ]
        
        try:
            addon_prefs = context.preferences.addons['Pak'].preferences
        except KeyError:
            return items
        
        strings = addon_prefs.bundle_strings

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
                ('A', "A", "")),
		description = "",
		default = 'R',
    )

    def execute(self, context):
        #print(self)
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        # This feels wrong, but I couldn't work out a nicer way D:
        slot_name = self.GetSlots(context)[int(self.slots)][1]
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
            case _:
                pass
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

    def draw_header_preset(self, _context):
        PAK_PT_ImagePack_PresetsOps.draw_panel_header(self.layout)

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        try:
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except KeyError:
            return

        pack_test = layout.column(align = False)
        pack_test.use_property_split = True
        pack_test.use_property_decorate = False
        pack_test.active = file_data.enable_bundles

        pack_test_r_source = pack_test.row(align = True)
        pack_test_r_source.prop(file_data, "pack_r_source")
        pack_test_r_source.operator_menu_enum('scene.pak_imagepack_addslotname', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'R'
        
        pack_test_r_channel = pack_test.row(align = False)
        pack_test_r_channel.prop(file_data, "pack_r_channel", expand = True)
        pack_test.prop(file_data, "pack_r_invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_g_source = pack_test.row(align = True)
        pack_test_g_source.prop(file_data, "pack_g_source")
        pack_test_g_source.operator_menu_enum('scene.pak_imagepack_addslotname', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'G'
        
        pack_test_g_source = pack_test.row(align = False)
        pack_test_g_source.prop(file_data, "pack_g_channel", expand = True)
        pack_test.prop(file_data, "pack_g_invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_b_source = pack_test.row(align = True)
        pack_test_b_source.prop(file_data, "pack_b_source")
        pack_test_b_source.operator_menu_enum('scene.pak_imagepack_addslotname', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'B'
        
        pack_test_b_source = pack_test.row(align = False)
        pack_test_b_source.prop(file_data, "pack_b_channel", expand = True)
        pack_test.prop(file_data, "pack_b_invert")
        pack_test.separator()
        pack_test.separator()

        pack_test_a_source = pack_test.row(align = True)
        pack_test_a_source.prop(file_data, "pack_a_source")
        pack_test_a_source.operator_menu_enum('scene.pak_imagepack_addslotname', "slots",
                                              text = "",
                                              icon = "ADD").path_target = 'A'
        
        pack_test_a_source = pack_test.row(align = False)
        pack_test_a_source.prop(file_data, "pack_a_channel", expand = True)
        pack_test.prop(file_data, "pack_a_invert")
        pack_test.separator()
        pack_test.separator()

        pack_test.prop(file_data, "packed_image_suffix")
        pack_test.separator()
        pack_test.separator()

        # Image Pack Operators
        bake_menu_box = layout.box()
        bake_menu = bake_menu_box.column(align = False)
        bake_menu.use_property_split = True
        bake_menu.use_property_decorate = False
        bake_menu.active = file_data.enable_bundles
        
        PAK_UI_CreateSelectionHeader(bake_menu, file_data)
        bake_menu.active = False
        bake_menu.prop(file_data, "overwrite_image_pack")
        bake_menu.separator()
        bake_menu.operator("scene.cap_createimagepack")

# //////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////
# IMAGE PACK OPERATOR

class PAK_OT_CreateImagePack(Operator):
    """Creates a new packed image based on channels from existing images found within a bundle"""
    bl_idname = "scene.cap_createimagepack"
    bl_label = "Create Packed Image"

    def execute(self, context):

        return {'FINISHED'}

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
        except:
            return {'CANCELLED'}
        
        bundle_strings = [t.text for t in addon_prefs.bundle_strings]
        
        def get_image_for_slot(bundle, sources):
            if sources == "":
                return None
            
            sources = sources.replace(",", "")
            slot_strings = sources.split()

            for bundle_item in bundle.bundle_items:
                filename = os.path.splitext(bundle_item.tex.name)[0]
                match = next(filter(filename.endswith, slot_strings), None)

                if match:
                    return bundle_item.tex
                
        # Thanks!
        # https://blender.stackexchange.com/questions/40562/how-to-combine-images-using-python
        def np_array_from_image(img):
            return np.array(img.pixels[:])

        bundle = file_data.bundles[file_data.bundles_list_index]

        # Access source, channel and inversion data
        source_r = get_image_for_slot(bundle, file_data.pack_r_source)
        source_g = get_image_for_slot(bundle, file_data.pack_g_source)
        source_b = get_image_for_slot(bundle, file_data.pack_b_source)
        source_a = get_image_for_slot(bundle, file_data.pack_a_source)

        channel_r = file_data.pack_r_channel
        channel_g = file_data.pack_g_channel
        channel_b = file_data.pack_b_channel
        channel_a = file_data.pack_a_channel
        
        # Work out what valid sources we have to operate on.


        r_pixels = np_array_from_image(source_b)
        
        print(r_pixels[0:20])
        print(source_a)



        return {'FINISHED'}