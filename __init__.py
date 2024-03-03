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
    "name": "PakPal",
    "author": "Takanu Kyriako.",
    "version": (0, 9, 9),
    "blender": (4, 0, 0),
    "location": "Properties > Output",
    "wiki_url": "https://github.com/Takanu/PakPal",
    "description": "Helps you prepare and batch export images loaded in Blender",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
from . import auto_load
from bpy.types import AddonPreferences, PropertyGroup, UIList
from bpy.props import PointerProperty,  StringProperty, CollectionProperty

from .main_menu import PAK_UI_CreatePakData
from .material_slots import CreateDefaultMaterialSlotNames

auto_load.init()

from .properties import *

class PAK_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    # The name for the empty object that exists to store .blend file data
    # WARNING: A string version is used for Image Pack Presets
    pak_filedata_name: StringProperty(
        name = "Dummy Datablock Name",
        description = "The dummy block being used to store file data, as Blender has no mechanism for adding blend data properties",
        default = ">PakPal Blend File Data<"
    )

    # material slot names are used to bundle images together in the interface and for 
    # operations like image packing
    material_slot_names: CollectionProperty(type = PAK_MaterialSlot)
    material_slot_names_list_index: IntProperty(default = 0)


    def draw(self, context):
        layout = self.layout
        
        addon_options = layout.column(align = True)
        addon_options.operator("pak.reset_properties")



def register():
    auto_load.register()

    # Assign datablocks now all classes have been registered.
    bpy.types.Image.PAK_Img = PointerProperty(name = 'PakPal Texture Data', 
                                                type = PAK_Image)
    bpy.types.Object.PAK_FileData = PointerProperty(name = 'PakPal File Data', 
                                                        type = PAK_FileData)
    
    bpy.utils.register_class(PAK_AddonPreferences)
    CreateDefaultMaterialSlotNames()

    

def unregister():
    bpy.utils.unregister_class(PAK_AddonPreferences)

    del bpy.types.Object.PAK_FileData
    del bpy.types.Image.PAK_Img

    # TODO: Delete the PakPal Preview texture.
    # TODO: Delete the Compositor nodes.

    auto_load.unregister()

