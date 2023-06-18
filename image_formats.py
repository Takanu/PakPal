
import bpy
import mathutils

from bpy.types import Menu, Panel, Operator

# https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html#imageformatsettings-bpy-struct

# NOTE: Color management has been disabled for now, color alteration
# is removed when creating and rendering new images.



# This is run when PakPal data is first created to make two unique nodes in the scene.
class PAK_OT_CreateImageFormatData(Operator):
     """(INTERNAL OPERATOR) Creates image format data for PakPal if none exist"""
     bl_idname = "pak.create_image_format_data"
     bl_label = "Create PakPal Image Data"

     def execute(self, context):

        try:
            addon_prefs = bpy.context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return False

        file_data.scene_data = bpy.context.scene
        data_scene = file_data.scene_data

        # BUILD DATA
        # build the nodes and place them away from the center of the graph.
        data_scene.use_nodes = True
        tree = data_scene.node_tree
        links = tree.links

        try:
            frame = data_scene.node_tree.nodes[addon_prefs.frame_node_name]
        except:
            frame = tree.nodes.new(type = 'NodeFrame')
            frame.name = addon_prefs.frame_node_name
            frame.label = "PakPal File Format Storage"
            frame.location = -500,500
            frame.use_custom_color = True
            frame.color = mathutils.Color((0.0, 0.3, 1.0))

        try:
            packer_node = data_scene.node_tree.nodes[addon_prefs.packer_node_name]
        except:
            packer_node = tree.nodes.new(type = 'CompositorNodeOutputFile')
            packer_node.name = addon_prefs.packer_node_name
            packer_node.label = addon_prefs.packer_node_name
            packer_node.location = -500,500
            packer_node.parent = frame
        
        try:
            slot_node = data_scene.node_tree.nodes[addon_prefs.slots_node_name]
        except:
            slot_node = tree.nodes.new(type = 'CompositorNodeOutputFile')
            slot_node.name = addon_prefs.packer_node_name
            slot_node.label = addon_prefs.packer_node_name
            slot_node.location = -200,500
            slot_node.parent = frame
        

        # Get node using:
        # data_scene.node_tree.nodes[addon_prefs.packer_node_name]

        return {'FINISHED'}
               
        


# Because a separate property is required to unpack and save a ImageFormatSettings type,
# we need to manually transfer properties
# 
# MAINTENANCE : This will need to be checked regularly.
# https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings
#
# This saves the properties from the in-built type to a provided PAK_ImageFormat property.
def SaveImageFormat(image_format_prop, image_format_type):
    image_format_prop.cineon_black = image_format_type.cineon_black
    image_format_prop.cineon_gamma = image_format_type.cineon_gamma
    image_format_prop.cineon_white = image_format_type.cineon_white

    image_format_prop.color_depth = image_format_type.color_depth
    image_format_prop.color_management = image_format_type.color_management
    image_format_prop.color_mode = image_format_type.color_mode

    image_format_prop.compression = image_format_type.compression
    ### Dont think I need it (readonly)
    # image_format_prop.display_settings = image_format_type.display_settings

    image_format_prop.exr_codec = image_format_type.exr_codec
    image_format_prop.file_format = image_format_type.file_format

    ### (READONLY)
    # image_format_prop.has_linear_colorspace = image_format_type.has_linear_colorspace

    image_format_prop.jpeg2k_codec = image_format_type.jpeg2k_codec
    ### "Output color space settings" (readonly)
    # image_format_prop.linear_colorspace_settings = image_format_type.linear_colorspace_settings
    image_format_prop.quality = image_format_type.quality
    
    ### I dont think I need this?
    # image_format_prop.stereo_3d_format = image_format_type.stereo_3d_format

    image_format_prop.tiff_codec = image_format_type.tiff_codec
    image_format_prop.use_cineon_log = image_format_type.use_cineon_log

    image_format_prop.use_jpeg2k_cinema_48 = image_format_type.use_jpeg2k_cinema_48
    image_format_prop.use_jpeg2k_cinema_preset = image_format_type.use_jpeg2k_cinema_preset
    image_format_prop.use_jpeg2k_ycc = image_format_type.use_jpeg2k_ycc

    image_format_prop.use_preview = image_format_type.use_preview
    image_format_prop.use_zbuffer = image_format_type.use_zbuffer

    # image_format_prop.view_settings = image_format_type.view_settings
    # image_format_prop.views_format = image_format_type.views_format




# This loads the properties from a provided PAK_ImageFormat property to the in-built type.
def LoadImageFormat(image_format_prop, image_format_type):
    pass




# This transfers image format data between ImageFormatSettings types.
def TransferImageFormatSettings(source, target):
    target.cineon_black = source.cineon_black
    target.cineon_gamma = source.cineon_gamma
    target.cineon_white = source.cineon_white

    target.color_depth = source.color_depth
    target.color_management = source.color_management
    target.color_mode = source.color_mode

    target.compression = source.compression
    ### Dont think I need it (readonly)
    # image_format_prop.display_settings = image_format_type.display_settings

    target.exr_codec = source.exr_codec
    target.file_format = source.file_format

    ### (READONLY)
    # target.has_linear_colorspace = source.has_linear_colorspace

    target.jpeg2k_codec = source.jpeg2k_codec
    ### "Output color space settings" (readonly)
    # image_format_prop.linear_colorspace_settings = image_format_type.linear_colorspace_settings
    target.quality = source.quality
    
    ### I dont think I need this?
    # image_format_prop.stereo_3d_format = image_format_type.stereo_3d_format

    target.tiff_codec = source.tiff_codec
    target.use_cineon_log = source.use_cineon_log

    target.use_jpeg2k_cinema_48 = source.use_jpeg2k_cinema_48
    target.use_jpeg2k_cinema_preset = source.use_jpeg2k_cinema_preset
    target.use_jpeg2k_ycc = source.use_jpeg2k_ycc

    target.use_preview = source.use_preview
    target.use_zbuffer = source.use_zbuffer

    # image_format_prop.view_settings = image_format_type.view_settings
    # image_format_prop.views_format = image_format_type.views_format



def UI_CreateFormatData(layout):

    # UI Prompt for when the PakPal file data can no longer be found.
    format_box = layout.box()
    format_info = format_box.column(align = True)
    format_info.label(text = "PakPal image format settings cannot be found.",
                      icon = "ERROR")
    
    format_desc = layout.column(align = True)
    format_desc.separator()
    format_desc.label(text = "You might have deleted the scene it was stored in (thats fine!)")
    format_desc.label(text = "Press the button below to rebuild this data in the current scene.")
    format_desc.separator()

    format_desc.separator()
    format_desc.operator("pak.create_image_format_data")

    return

# When using image.save_render it doesn't add the file extension for you, so
# you need this.
# MAINTENANCE : This will need to be checked regularly.
def GetImageFileExtension(file_format):

    match file_format:
        case 'BMP':
            return '.jpg'
        case 'IRIS':
            return '.iris'
        case 'PNG':
            return '.png'
        case 'JPEG':
            return '.jpg'
        case 'JPEG2000':
            return '.jp2'
        
        case 'TARGA':
            return '.tga'
        case 'TARGA_RAW':
            return '.tga'
        case 'CINEON':
            return '.cin'
        case 'DPX':
            return '.dpx'
        case 'OPEN_EXR_MULTILAYER':
            return '.exr'
        case 'OPEN_EXR':
            return '.exr'
        
        case 'HDR':
            return '.hdri'
        case 'TIFF':
            return '.tiff'
        case 'WEBP':
            return '.webp'
        case _:
            return None