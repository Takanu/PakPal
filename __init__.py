# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#This states the metadata for the plugin
bl_info = {
    "name": "Pak",
    "author": "Takanu Kyriako.",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "Properties > Output",
    "wiki_url": "https://github.com/Takanu/Pak",
    "description": "Batch export textures used in scenes",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
from . import auto_load
from bpy.types import AddonPreferences, PropertyGroup, UIList
from bpy.props import PointerProperty,  StringProperty, CollectionProperty

from .user_interface import PAK_CreatePakDataUI

auto_load.init()

from .properties import *

class PAK_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    # The name for the empty object that exists to store .blend file data
    default_datablock: StringProperty(
        name = "Dummy Datablock Name",
        description = "The dummy block being used to store file data, as Blender has no mechanism for adding blend data properties",
        default = ">Pak Blend File Data<"
    )

    bundle_strings: CollectionProperty(type = PAK_BundleString)

    bundle_strings_list_index: IntProperty(default = 0)

    def draw(self, context):
        layout = self.layout

        try:
            file_data = bpy.data.objects[self.default_datablock].PAK_FileData
        except:
            PAK_CreatePakDataUI(layout)
            return

        bundle_strings_box = layout.box()
        
        bundle_strings_title = bundle_strings_box.row(align= True)
        bundle_strings_title.label(text= "Bundle Strings", icon = "PRESET")
        bundle_strings_title.operator("scene.cap_tut_bundlestrings", text = "", icon = "HELP")
        
        
        bundle_strings_area = bundle_strings_box.row(align = False)
        bundle_strings_list = bundle_strings_area.column(align = True)
        bundle_strings_list.template_list("PAK_UL_BundleStringList", "default", self, "bundle_strings", 
                                          self, "bundle_strings_list_index", 
                                          rows = 3, maxrows = 6)
        bundle_strings_list.separator()

        bundle_strings_ops = bundle_strings_area.column(align = True)
        bundle_strings_ops.operator("scene.pak_addbundlestring", text= "", icon = "ADD")
        bundle_strings_ops.operator("scene.pak_deletebundlestring", text= "", icon = "REMOVE")


# This creates a list of commonly used bundle strings when first registering Pak.
def CreateBundleStrings():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    new_string = addon_prefs.bundle_strings.add()
    new_string.text = "BaseColor"
    new_string = addon_prefs.bundle_strings.add()
    new_string.text = "Height"
    new_string = addon_prefs.bundle_strings.add()
    new_string.text = "Metallic"
    new_string = addon_prefs.bundle_strings.add()
    new_string.text = "Normal"
    new_string = addon_prefs.bundle_strings.add()
    new_string.text = "Roughness"


def register():
    auto_load.register()

    # Assign datablocks now all classes have been registered.
    bpy.types.Image.PAK_Tex = PointerProperty(name = 'Pak Texture Data', 
                                                type = PAK_Texture)
    bpy.types.Object.PAK_FileData = PointerProperty(name = 'Pak File Data', 
                                                        type = PAK_FileData)
    
    bpy.utils.register_class(PAK_AddonPreferences)
    CreateBundleStrings()

def unregister():
    bpy.utils.unregister_class(PAK_AddonPreferences)

    del bpy.types.Object.PAK_FileData
    del bpy.types.Image.PAK_Tex

    auto_load.unregister()

