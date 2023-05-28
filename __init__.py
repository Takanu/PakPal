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
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import PointerProperty

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

def register():
    auto_load.register()

    bpy.utils.register_class(PAK_AddonPreferences)
    
    # Assign datablocks now all classes have been registered.
    bpy.types.Image.PAK_Tex = PointerProperty(name = 'Pak Texture Data', 
                                                type = PAK_Texture)
    bpy.types.Object.PAK_FileData = PointerProperty(name = 'Pak File Data', 
                                                        type = PAK_FileData)

def unregister():
    del bpy.types.Object.PAK_FileData
    del bpy.types.Image.PAK_Tex

    bpy.utils.unregister_class(PAK_AddonPreferences)

    auto_load.unregister()
