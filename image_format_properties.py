import bpy
from bpy.types import AddonPreferences, PropertyGroup, ImageFormatSettings

from bpy.props import (
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    StringProperty, 
    PointerProperty, 
    CollectionProperty, 
    EnumProperty,
)

def PAK_Update_ImageFormatProxies(self, context):

    addon_prefs = context.preferences.addons[__package__].preferences
    file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    current_format = file_data.formats[file_data.formats_list_index]

    # TODO: Different formats MUST have certain color depths or modes set when
    # no options are available.

    match current_format.file_format:
        case 'BMP':
            current_format.color_mode = current_format.proxy_color_bw_rgb
        case 'PNG':
            current_format.color_depth = current_format.proxy_color_8_16
        case 'JPEG':
            current_format.color_depth = '8'
            current_format.color_mode = current_format.proxy_color_bw_rgb
        case 'JPEG2000':
            current_format.color_depth = current_format.proxy_color_8_16
        

        case 'TARGA':
            pass
        case 'TARGA_RAW':
            pass
        

        case 'HDR':
            current_format.color_mode = current_format.proxy_color_bw_rgb
        case 'TIFF':
            current_format.color_depth = current_format.proxy_color_8_16
        case 'WEBP':
            pass
        case _:
            pass

# As of 3.5 PointerProperty types currently only apply to ID and PropertyGroup subclasses 
# If this changes in a future version, replace this!
# TODO : This will need to be checked regularly.

# https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings
class PAK_ImageFormat(PropertyGroup):

    name: StringProperty(
        name = "Name",
        default = "",
    )

    file_format: EnumProperty(
        name = "File Format",
        items = (
            ('BMP', 'BMP', ''),
            # ('IRIS', 'Iris', ''),
            ('PNG', 'PNG', ''),
            ('JPEG', 'JPEG', ''),
            ('JPEG2000', 'JPEG 2000', ''),

            ('TARGA', 'Targa', ''),
            ('TARGA_RAW', 'Targa RAW', ''),
            # ('CINEON', 'Iris', ''),
            # ('DPX', 'DPX', ''),
            # ('OPEN_EXR_MULTILAYER', 'OpenEXR Multilayer', ''),
            # ('OPEN_EXR', 'BMP', ''),

            ('HDR', 'Radiance HDR', ''),
            ('TIFF', 'TIFF', ''),
            ('WEBP', 'WebP', ''),
        ),
        default = 'PNG',
        update = PAK_Update_ImageFormatProxies,
    )

    
    # Currently not in use to simplify the custom interface wrapper.
    cineon_black: IntProperty()
    cineon_gamma: FloatProperty()
    cineon_white: IntProperty()

    color_depth: EnumProperty(
        name = "Color Depth",
        items = (
            ('8', '8', ""),
            ('10', '10', ""),
            ('12', '12', ""),
            ('16', '16', ""),
            ('32', '32', ""),
        ),
        default = '16',
    )

    # can I just use a string property?  OwO
    # TODO: Enable color management settings
    color_management: EnumProperty(
        name = "Color Management",
        items = (
            ('FOLLOW_SCENE', "Follow Scene", ''),
            ('OVERRIDE', "Override", ''),
        ),
        default = 'FOLLOW_SCENE',
    )

    color_mode: EnumProperty(
        name = 'Color',
        items = (
            ('BW', 'BW', ''),
            ('RGB', 'RGB', ''),
            ('RGBA', 'RGBA', ''),
        ),
        default = 'RGBA',
    )

    compression: IntProperty(
        name = 'Compression',
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE',
        default = 0,
    )

    # (readonly)
    # display_settings - "Settings of devioce saved image would be displayed on"

    # exr_codec: StringProperty() - not in use
    # file_format: StringProperty() - replaced with an enum

    has_linear_colorspace: BoolProperty()

    # Only used for JPEG 2K
    jpeg2k_codec: EnumProperty(
        name = "Codec",
        items = (
            ('JP2', 'J2K', ''),
            ('J2K', 'J2K', ''),
        ),
        default = 'JP2',
    )

    # (readonly)
    # linear_colorspace_settings -= "Output color space settings", opaque type.

    quality: IntProperty(
        name = 'Quality',
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE',
        default = 50,
    )

    # (readonly)
    # stereo_3d_format - Another weird structure

    tiff_codec: EnumProperty(
        name = "Compression",
        items = (
            ('NONE', 'None', ''),
            ('DEFLATE', 'Deflate', ''),
            ('LZW', 'LZW', ''),
            ('PACKBITS', 'Pack Bits', ''),
        ),
        default = 'DEFLATE',
    )

    use_cineon_log: BoolProperty()

    use_jpeg2k_cinema_48: BoolProperty(
        name = 'Cinema (48)',
        default = False,
    )
    use_jpeg2k_cinema_preset: BoolProperty(
        name = 'Cinema',
        default = False,
    )
    use_jpeg2k_ycc: BoolProperty(
        name = 'YCC',
        default = False,
    )

    use_preview: BoolProperty() # saves JPG images of animations to the same directory

    # (readonly)
    # view_settings - appears to be the color management settings we're interested in
    # (readonly)
    # views_format - For stereo output, we don't care.


    # //////////////////////////////
    # PROXY PROPERTIES

    # These are used for the interface and map back to the core available settings.
    proxy_color_bw_rgb: EnumProperty(
        name = 'Color',
        items = (
            ('BW', 'BW', ''),
            ('RGB', 'RGB', ''),
        ),
        default = 'RGB',
        update = PAK_Update_ImageFormatProxies,
    )

    proxy_color_rgb_rgba: EnumProperty(
        name = 'Color',
        items = (
            ('RGB', 'RGB', ''),
            ('RGBA', 'RGBA', ''),
        ),
        default = 'RGBA',
        update = PAK_Update_ImageFormatProxies,
    )

    proxy_color_8_16: EnumProperty(
        name = 'Color Depth',
        items = (
            ('8', "8", ""),
            ('16', "16", ""),
            ),
        default = '16',
        update = PAK_Update_ImageFormatProxies,
    )   

    proxy_color_8_12_16: EnumProperty(
        name = 'Color Depth',
        items = (
            ('8', "8", ""),
            ('12', "12", ""),
            ('16', "16", ""),
            ),
        default = '16',
        update = PAK_Update_ImageFormatProxies,
    )   

    proxy_color_8_10_12_16: EnumProperty(
        name = 'Color Depth',
        items = (
            ('8', "8", ""),
            ('10', "10", ""),
            ('12', "12", ""),
            ('16', "16", ""),
            ),
        default = '16',
        update = PAK_Update_ImageFormatProxies,
    )   

    proxy_color_16_32: EnumProperty(
        name = 'Color Depth',
        items = (
            ('16', "Float (Half)", ""),
            ('32', "Float (Full)", "")
            ),
        default = '16',
        update = PAK_Update_ImageFormatProxies,
    )   




# Because a separate property is required to unpack and save a ImageFormatSettings type,
# we need to manually transfer properties
# 
# TODO : This will need to be checked regularly.
# https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings
#
# This transfers a PAK_ImageFormat type to the ImageFormatSettings target.
def LoadImageFormat(pak_format : PAK_ImageFormat, blender_format : ImageFormatSettings):
    
    blender_format.cineon_black = pak_format.cineon_black
    blender_format.cineon_gamma = pak_format.cineon_gamma
    blender_format.cineon_white = pak_format.cineon_white

    blender_format.color_depth = pak_format.color_depth
    blender_format.color_management = pak_format.color_management
    blender_format.color_mode = pak_format.color_mode

    blender_format.compression = pak_format.compression
    ### Dont think I need it (readonly)
    # blender_format.display_settings = pak_format.display_settings

    ### not in use
    # blender_format.exr_codec = pak_format.exr_codec
    blender_format.file_format = pak_format.file_format

    ### (READONLY)
    # blender_format.has_linear_colorspace = pak_format.has_linear_colorspace

    blender_format.jpeg2k_codec = pak_format.jpeg2k_codec
    ### "Output color space settings" (readonly)
    # blender_format.linear_colorspace_settings = pak_format.linear_colorspace_settings
    blender_format.quality = pak_format.quality
    
    ### I dont think I need this?
    # blender_format.stereo_3d_format = pak_format.stereo_3d_format

    blender_format.tiff_codec = pak_format.tiff_codec
    blender_format.use_cineon_log = pak_format.use_cineon_log

    blender_format.use_jpeg2k_cinema_48 = pak_format.use_jpeg2k_cinema_48
    blender_format.use_jpeg2k_cinema_preset = pak_format.use_jpeg2k_cinema_preset
    blender_format.use_jpeg2k_ycc = pak_format.use_jpeg2k_ycc

    blender_format.use_preview = pak_format.use_preview

    # blender_format.view_settings = pak_format.view_settings
    # blender_format.views_format = pak_format.views_format



# When using image.save_render it doesn't add the file extension for you, so
# you need this.
# NOTE : This will need to be checked regularly.
def GetImageFileExtension(file_format : str):

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
        

# This creates an interface to mimic the ImageFormatSettings menu of Blender.
# This is required to the read-only nature of the format and the inability
# to use it as a PointerProperty.
#
# NOTE : This will need to be checked regularly.
def UI_CreateFormatSettings(layout, format_settings : PAK_ImageFormat):

    layout.prop(format_settings, 'file_format')

    match format_settings.file_format:
        case 'BMP':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'proxy_color_bw_rgb', expand = True)
        case 'PNG':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
            color_depth_ui = layout.row(align = True)
            color_depth_ui.prop(format_settings, 'proxy_color_8_16', expand = True)
            layout.prop(format_settings, 'compression')
        case 'JPEG':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'proxy_color_bw_rgb', expand = True)
            layout.prop(format_settings, 'quality')
        case 'JPEG2000':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
            color_depth_ui = layout.row(align = True)
            color_depth_ui.prop(format_settings, 'proxy_color_8_12_16', expand = True)
            layout.prop(format_settings, 'quality')
            layout.prop(format_settings, 'jpeg2k_codec')
            layout.prop(format_settings, 'use_jpeg2k_cinema_48')
            layout.prop(format_settings, 'use_jpeg2k_cinema_preset')
            layout.prop(format_settings, 'use_jpeg2k_ycc')
        

        case 'TARGA':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
        case 'TARGA_RAW':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
        

        case 'HDR':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'proxy_color_bw_rgb', expand = True)
        case 'TIFF':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
            color_depth_ui = layout.row(align = True)
            color_depth_ui.prop(format_settings, 'proxy_color_8_16', expand = True)
            layout.prop(format_settings, 'tiff_codec')
        case 'WEBP':
            color_mode_ui = layout.row(align = True)
            color_mode_ui.prop(format_settings, 'color_mode', expand = True)
            layout.prop(format_settings, 'quality')
        case _:
            layout.label(text = "This shouldnt be here!")
            # layout.prop(format_settings, 'color_mode')
            # layout.prop(format_settings, 'color_depth')
            

    pass