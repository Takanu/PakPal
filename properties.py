
import bpy
from bpy.types import AddonPreferences, PropertyGroup
from .update import *
from .image_format_properties import PAK_ImageFormat

from bpy.props import (
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    StringProperty, 
    PointerProperty, 
    CollectionProperty, 
    EnumProperty,
)

def GetExportLocations(scene, context):

    items = [
        ('0', "None", "No export location has been set", 0),
    ]
    
    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        
    except KeyError:
        return items

    for i,x in enumerate(file_data.locations):
        items.append((str(i+1), x.name, x.name, i+1))

    return items

def GetImageFormats(scene, context):

    items = [
        ('0', "Original Format", "The image will be saved with the same format and settings as the original image", 0),
    ]
    
    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        
    except KeyError:
        return items

    for i,x in enumerate(file_data.formats):
        items.append((str(i+1), x.name, x.name, i+1))

    return items


class PAK_Image(PropertyGroup):
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
        items = GetExportLocations,
    )

    export_format: EnumProperty(
        name = "Export Format",
        description = "Set the export format that will be used when exporting a texture.  This will NOT change the file format of the image as it is currently stored",
        items = GetImageFormats,
    )
    

class PAK_ImageItem(PropertyGroup):
    """
    Defines a single texture within a PAK_ImageBundle.
    It just wraps an image type in a PropertyGroup as Blender is a bit dumb with collections.
    """

    tex: PointerProperty(
        type = bpy.types.Image,
        name = "Texture",
        description = "A pointer for the texture this list item represents",
    )


class PAK_ImageBundle(PropertyGroup):
    """
    Define an object as a list property, for use when displaying objects in the user interface
    """

    pak_items: CollectionProperty(type = PAK_ImageItem)

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
        items = GetExportLocations,
    )

    export_format: EnumProperty(
        name = "Export Format",
        description = "Set the export format that will be used when exporting a texture.  This will NOT change the file format of the image as it is currently stored",
        update = PAK_Update_TextureListItem_ExportFormat,        
        items = GetImageFormats,
    )

    # Used for multi-select mode.
    is_selected: BoolProperty(
        default = False,
        update = PAK_Update_TextureListItem_IsSelected,
    )


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
    Everything PakPal needs to preserve as part of the file.
    """

    # if true, this object is the empty created for the purposes of storing preset data.
    is_file_data: BoolProperty(default = False)

    # the available images for export
    bundles: CollectionProperty(type = PAK_ImageBundle)

    ## The index of the currently selected collection from the UI list.  Will be -1 if not selected.
    bundles_list_index: IntProperty(
        name = "Image",
        description = "This is an image datablock stored in the currently open .blend file",
        default = 0,
        update = PAK_Update_TextureList_Preview
    )

    # the available export locations
    locations: CollectionProperty(type = PAK_ExportLocations)
    ## The index of the currently selected export collection from the UI list.  Will be -1 if not selected.
    locations_list_index: IntProperty(default = 0)

    # the available export formats
    formats: CollectionProperty(type = PAK_ImageFormat)
    formats_list_index: IntProperty(default = 0)

    case_sensitive_matching: BoolProperty(
        name = "Case Sensitive Matching",
        description = "If enabled, operations that use material slot names such as image packing and material bundling will perform material slot comparisons in a case sensitive manner"
    )

    # The scene used to store Compositor nodes in.
    scene_data: PointerProperty(
        type = bpy.types.Scene,
        name = "PakPal Scene Data Source",
        description = "Defines the scene used to store Compositor nodes used for managing Image Format settings"
    )

    ## HIDDEN PROPERTIES
    # (these are activated with operators due to styling issues)
    
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

    ## TEXTURE LIST OPTIONS
    # These appear in the dropdown

    show_material_count: BoolProperty(
        name = "Show Material Count",
        description = "Shows the number of materials an image uses",
        default = False,
    )

    show_user_count: BoolProperty(
        name = "Show User Count",
        description = "Shows the number of users an image has, including fake users",
        default = False,
    )

    show_fake_user: BoolProperty(
        name = "Show Fake Users",
        description = "Shows if an image has a fake user",
        default = False,
    )

    show_file_format: BoolProperty(
        name = "Show Format Type",
        description = "Shows the format of the image",
        default = False,
    )

    # if true, show hidden images in the list
    show_hidden: BoolProperty(
        name = "Show Hidden Images",
        description = "Enable or disable the ability to see hidden image blocks.  These might be used by other addons so be careful!",
        default = False,
        update = PAK_Update_RefreshList,
    )

    ## TEXTURE PREVIEW
    # (these are activated with operators due to styling issues)

    preview_tex: PointerProperty(
        type = bpy.types.Texture,
        name = "Preview Texture",
        description = "Used to preview images in the interface"
    )

    preview_rgb: EnumProperty(
        name = "RGB Preview",
        options = {'ENUM_FLAG'},
        items = (('R', "", "", 'COLOR_RED', 1),
                ('G', "", "", 'COLOR_GREEN', 2),
                ('B', "", "", 'COLOR_BLUE', 100), # due to weird behaviour
        ),
        description = "Change how the preview displays different color channels (alpha display is currently unsupported due to inbuilt image preview limitations)",
        default = {'R', 'G', 'B'},
        update = PAK_Update_TextureList_PreviewColor
    )

    

    # ////////////////////////////////////////////////////////////////////
    # ////////////////////////////////////////////////////////////////////
    ## PROXIES
    # These are used for multi-select operations and UI enhancements.

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
        items = GetExportLocations,
        update = PAK_Update_ExportLocation,
    )

    proxy_export_format: EnumProperty(
        name = "Export Format",
        description = "Set the export format that will be used when exporting a texture.  This will NOT change the file format of the image as it is currently stored",
        items = GetImageFormats,
        update = PAK_Update_ExportFormat,
    )

    # ////////////////////////////////////////////////////////////////////
    # ////////////////////////////////////////////////////////////////////
    # IMAGE PACKING
    # These options are used when performing a channel mix operation

    pack_format: PointerProperty(type=PAK_ImageFormat)

    pack_r_source: StringProperty(
        name = "Red Source Slot Name",
        description = "Set the name of the material slot that will be used as a source for the new image's red channel (if it can be found within a bundle).  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_g_source: StringProperty(
        name = "Green Source Slot Name",
        description = "Set the name of the material slot that will be used as a source for the new image's green channel (if it can be found within a bundle).  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_b_source: StringProperty(
        name = "Blue Source Slot Name",
        description = "Set the name of the material slot that will be used as a source for the new image's blue channel (if it can be found within a bundle).  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )

    pack_a_source: StringProperty(
        name = "Alpha Source Slot Name",
        description = "Set the name of the material slot that will be used as a source for the new image's alpha channel (if it can be found within a bundle).  Multiple slot names can be defined but only the first one found in a image bundle will be used",
        default = ""
    )


    pack_r_channel: EnumProperty(
		name = " ",
		items = (('R', "R", "Use the red channel from the source material slot as the new packed image's red channel"),
			    ('G', "G", "Use the green channel from the source material slot as the new packed image's red channel"),
			    ('B', "B", "Use the blue channel from the source material slot as the new packed image's red channel"),
                ('A', "A", "Use the alpha channel from the source material slot as the new packed image's red channel")),
		description = "",
		default = 'R',
	)

    pack_g_channel: EnumProperty(
		name = " ",
		items = (('R', "R", "Use the red channel from the source material slot as the new packed image's green channel"),
			    ('G', "G", "Use the green channel from the source material slot as the new packed image's green channel"),
			    ('B', "B", "Use the blue channel from the source material slot as the new packed image's green channel"),
                ('A', "A", "Use the alpha channel from the source material slot as the new packed image's green channel")),
		description = "",
		default = 'R',
	)

    pack_b_channel: EnumProperty(
		name = " ",
		items = (('R', "R", "Use the red channel from the source material slot as the new packed image's blue channel"),
			    ('G', "G", "Use the green channel from the source material slot as the new packed image's blue channel"),
			    ('B', "B", "Use the blue channel from the source material slot as the new packed image's blue channel"),
                ('A', "A", "Use the alpha channel from the source material slot as the new packed image's blue channel")),
		description = "",
		default = 'R',
	)

    pack_a_channel: EnumProperty(
		name = " ",
		items = (('R', "R", "Use the red channel from the source material slot as the new packed image's alpha channel"),
			    ('G', "G", "Use the green channel from the source material slot as the new packed image's alpha channel"),
			    ('B', "B", "Use the blue channel from the source material slot as the new packed image's alpha channel"),
                ('A', "A", "Use the alpha channel from the source material slot as the new packed image's alpha channel")),
		description = "",
		default = 'R',
	)

    pack_r_invert: BoolProperty(
        name = "Invert R Source",
        description = "Invert the source image output",
        default = False,
    )

    pack_g_invert: BoolProperty(
        name = "Invert G Source",
        description = "Invert the source image output",
        default = False,
    )

    pack_b_invert: BoolProperty(
        name = "Invert B Source",
        description = "Invert the source image output",
        default = False,
    )

    pack_a_invert: BoolProperty(
        name = "Invert A Source",
        description = "Invert the source image output",
        default = False,
    )

    packed_image_suffix: StringProperty(
        name = "Packed Image Suffix",
        description = "Set the suffix the new image will be given.  The base name of the new image will be the same as the base name for the Bundle",
        default = "",
    )
    overwrite_image_pack: BoolProperty(
        name = "Overwrite Existing Image",
        description = "If an image is found with the same name in the Blend file, the new packed image will replace it",
        default = True,
    )

    add_fake_user: BoolProperty(
        name = "Add Fake User",
        description = "Adds a fake user to any generated packed images to prevent them from disappearing when the blend file is closed",
        default = True,
    )

    temp_bake_path: StringProperty(
        name = "Temp Save Location",
        description = "A temporary location used to save packed images.  Either due to Blender limitations or a skill issue, PakPal needs to save images somewhere before reloading and saving them in the blend file",
        default = "//Pak_Cache\\",
        subtype = "FILE_PATH"
    )


class PAK_MaterialSlot(PropertyGroup):

    text: StringProperty(
        name = "Bundle Text",
        description = "",
        default = "",
    )



