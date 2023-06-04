
import bpy
from bpy.types import AddonPreferences, PropertyGroup
from .update import *

from bpy.props import (
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    StringProperty, 
    PointerProperty, 
    CollectionProperty, 
    EnumProperty,
)

def GetLocationPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
    ]

    preferences = context.preferences
    addon_prefs = preferences.addons['Pak'].preferences
    try:
        file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
    except KeyError:
        return items

    u = 1

    for i,x in enumerate(file_data.locations):
        items.append((str(i+1), x.name, x.name, i+1))

    return items



class PAK_Texture(PropertyGroup):
    """
    Define an object as a list property, for use when displaying objects 
    in the user interface.
    """

    enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enable or disable the texture for export",
        default = False,
    )

    export_location: EnumProperty(
        name = "Export Location",
        description = "Set the file path that the texture will be exported to",
        items = GetLocationPresets,
    )
    

class PAK_TextureItem(PropertyGroup):
    """
    Defines a single texture within a PAK_TextureListItem.
    It just wraps an image type in a PropertyGroup as Blender is a bit dumb with collections.
    """

    tex: PointerProperty(
        type = bpy.types.Image,
        name = "Texture",
        description = "A pointer for the texture this list item represents",
    )


class PAK_TextureListItem(PropertyGroup):
    """
    Define an object as a list property, for use when displaying objects in the user interface
    """

    bundle_items: CollectionProperty(type = PAK_TextureItem)

    name: StringProperty(
        name = "Texture/Bundle Name",
        description = "",
        default = "",
        update = PAK_Update_TextureListItem_Name
    )

    enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enable or disable the texture for export",
        default = False,
        update = PAK_Update_TextureListItem_EnableExport,
    )

    export_location: EnumProperty(
        name = "Export Location",
        description = "Set the file path that the texture will be exported to",
        update = PAK_Update_TextureListItem_ExportLocation,
        items = GetLocationPresets,
        
    )

    # Used for multi-select mode.
    is_selected: BoolProperty(default = False)


class PAK_ExportLocations(PropertyGroup):
    # Defines a single export location that can be reused across multiple textures

    name: StringProperty(
        name = "",
        description = "The name of the export location"
    )

    path: StringProperty(
        name = "",
        description = "The file path used to export images to",
        default = "",
        subtype = "FILE_PATH"
    )


class PAK_FileData(PropertyGroup):
    """
    Everything Pak needs to preserve as part of the file.
    """

    # if true, this object is the empty created for the purposes of storing preset data.
    is_file_data: BoolProperty(default = False)

    # the available baking presets
    bundles: CollectionProperty(type = PAK_TextureListItem)

    ## The index of the currently selected collection from the UI list.  Will be -1 if not selected.
    bundles_list_index: IntProperty(default = 0)

    # the available baking presets
    locations: CollectionProperty(type = PAK_ExportLocations)

    ## The index of the currently selected collection from the UI list.  Will be -1 if not selected.
    locations_list_index: IntProperty(default = 0)
    
    # if true, images can be edited with a psuedo multiselect interface.
    enable_multiselect: BoolProperty(
        name = "Enable Multiselect",
        description = "When enabled, multiple textures can be selected and edited at the same time",
        default = False,
    )

    # if true, images can be edited with a psuedo multiselect interface.
    enable_bundles: BoolProperty(
        name = "Enable Bundles",
        description = "When enabled, textures sharing the same name but using common suffixes (like BaseColor, Height, etc) will be represented as a single entry in the list, and can be edited as a set of images",
        default = False,
        update = PAK_Update_EnableBundles,
    )

    
    ## PROXIES
    # These are used for multi-select operations.

    # Used during a refresh to prevent unnecessary update function triggers.
    is_internal_update: BoolProperty(default = False)

    proxy_enable_export: BoolProperty(
        name = "Enable Export",
        description = "Enable or disable the texture for export",
        default = False,
        update = PAK_Update_EnableExport,
    )

    proxy_export_location: EnumProperty(
        name = "Export Location",
        description = "Set the file path that the texture will be exported to",
        items = GetLocationPresets,
        update = PAK_Update_ExportLocation,
    )

    # CHANNEL MIXING
    # These options are used when performing a channel mix operation
    pack_r_source: StringProperty(
        name = "R Source Slots",
        description = "Set the texture slot that will be used as a source for the packed image's red channel if it can be found within a bundle.  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_g_source: StringProperty(
        name = "G Source Slots",
        description = "Set the texture slot that will be used as a source for the packed image's green channel if it can be found within a bundle.  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_b_source: StringProperty(
        name = "B Source Slots",
        description = "Set the texture slot that will be used as a source for the packed image's blue channel if it can be found within a bundle.  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_a_source: StringProperty(
        name = "A Source Slots",
        description = "Set the texture slot that will be used as a source for the packed image's alpha channel if it can be found within a bundle.  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )


    pack_r_channel: EnumProperty(
		name = " ",
		items = (('R', "R", ""),
			    ('G', "G", ""),
			    ('B', "B", ""),
                ('A', "A", "")),
		description = "",
		default = 'R',
	)

    pack_g_channel: EnumProperty(
		name = " ",
		items = (('R', "R", ""),
			    ('G', "G", ""),
			    ('B', "B", ""),
                ('A', "A", "")),
		description = "",
		default = 'R',
	)

    pack_b_channel: EnumProperty(
		name = " ",
		items = (('R', "R", ""),
			    ('G', "G", ""),
			    ('B', "B", ""),
                ('A', "A", "")),
		description = "",
		default = 'R',
	)

    pack_a_channel: EnumProperty(
		name = " ",
		items = (('R', "R", ""),
			    ('G', "G", ""),
			    ('B', "B", ""),
                ('A', "A", "")),
		description = "",
		default = 'R',
	)

    pack_r_invert: BoolProperty(
        name = "Invert R Source",
        description = "Invert the source image channel input",
        default = False,
    )

    pack_g_invert: BoolProperty(
        name = "Invert G Source",
        description = "Invert the source image channel input",
        default = False,
    )

    pack_b_invert: BoolProperty(
        name = "Invert B Source",
        description = "Invert the source image channel input",
        default = False,
    )

    pack_a_invert: BoolProperty(
        name = "Invert A Source",
        description = "Invert the source image channel input",
        default = False,
    )

    packed_image_suffix: StringProperty(
        name = "Result Image Suffix",
        description = "Set the suffix the new image will be given.  The base name will be the same as the one for the Bundle",
        default = "",
    )

    overwrite_image_pack: BoolProperty(
        name = "Overwrite Existing Image",
        description = "If an image is found with the same name in the Blend file, the new packed image will replace it",
        default = False,
    )

    add_fake_user: BoolProperty(
        name = "Add Fake User",
        description = "Adds a fake user to any generated packed images to prevent them from disappearing when the blend file is closed",
        default = False,
    )

    temp_bake_path: StringProperty(
        name = "Temporary Save Location",
        description = "A temporary location used to save packed images.  Pak needs to save images somewhere before reloading and saving them in the blend file",
        default = "//Pak_Cache\\",
        subtype = "FILE_PATH"
    )


class PAK_BundleString(PropertyGroup):

    text: StringProperty(
        name = "Bundle Text",
        description = "",
        default = "",
    )