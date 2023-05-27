

import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import (
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    StringProperty, 
    PointerProperty, 
    CollectionProperty, 
    EnumProperty,
)

# def GetLocationPresets(scene, context):

#     items = [
#         ("0", "None",  "", 0),
#     ]

#     preferences = context.preferences
#     addon_prefs = preferences.addons['Capsule'].preferences
#     try:
#         cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
#     except KeyError:
#         return items

#     u = 1

#     for i,x in enumerate(cap_file.location_presets):
#         items.append((str(i+1), x.name, x.name, i+1))

#     return items

class PAK_Texture(PropertyGroup):
    """
    Define an object as a list property, for use when displaying objects in the user interface
    """

    enable_export: BoolProperty(
        name = "",
        description = "Enable or disable the texture for export",
        default = False,
    )

    # export_location: EnumProperty(
    #     name = "Export Location",
    #     description = "Set the file path that the texture will be exported to",
    #     items = GetLocationPresets,
    # )

class PAK_TextureListItem(PropertyGroup):
    """
    Define an object as a list property, for use when displaying objects in the user interface
    """

    tex: PointerProperty(
        type = bpy.types.Image,
        name = "Texture",
        description = "A pointer for the texture this list item represents",
    )


class PAK_ExportLocations(PropertyGroup):
    # Defines a single export location that can be reused across multiple textures

    name: StringProperty(
        name = "",
        description = "The name of the export location"
    )

    path: StringProperty(
        name = "",
        description = "The file path used to export textures to",
        default = "",
        subtype = "FILE_PATH"
    )


class PAK_SceneData(PropertyGroup):
    """
    An assortment of user-interface states and the list of baking operations.
    """

    # the available baking presets
    tex_list: CollectionProperty(type = PAK_TextureListItem)

    ## The index of the currently selected collection from the UI list.  Will be -1 if not selected.
    selected_list_index: IntProperty(default = 0)


class PAK_FileData(PropertyGroup):
    """
    Everything Pak needs to preserve as part of the file.
    """

    # if true, this object is the empty created for the purposes of storing preset data.
    is_file_data: BoolProperty(default = False)

    # if true, images can be edited with a psuedo multiselect interface.
    enable_multiselect: BoolProperty(default = False)

    # the available baking presets
    locations: CollectionProperty(type = PAK_ExportLocations)
    




    