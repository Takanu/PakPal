
import bpy, os, platform

from datetime import datetime
from bpy.types import Operator, Panel, UIList

from .main_menu import PAK_UI_CreatePakData, PAK_UI_CreateSelectionHeader
from .export_locations import CreateFilePath, SubstituteNameCharacters, ReplacePathTags

def FindImageContext():
    """
    Builds and returns a context override for when you NEED TO MAKE SURE your operators
    are executing in an Image context.
    """

    def getArea(type):
        for screen in bpy.context.workspace.screens:
            for area in screen.areas:
                if area.type == type:
                    return area

    win      = bpy.context.window
    scr      = win.screen
    areas3d  = [getArea('VIEW_3D')]
    region   = [region for region in areas3d[0].regions if region.type == 'WINDOW']

    override = {'window':win,
                'screen':scr,
                'area'  :getArea('VIEW_3D'),
                'region':region[0],
                'scene' :bpy.context.scene,
                'space' :getArea('VIEW_3D').spaces[0],
                }
    
    return override

class PAK_PT_ExportOptionsMenu(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Options"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 1

    def draw(self, context):

        layout = self.layout

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except KeyError:
            PAK_UI_CreatePakData(layout)
            return
        
        selection_box = layout.box()
        selection_box_area = selection_box.column(align = True)
        selection_box_area.use_property_split = True
        selection_box_area.use_property_decorate = False

        PAK_UI_CreateSelectionHeader(selection_box_area, file_data)

        selection_options = layout.column(align = True)
        selection_options.use_property_split = True
        selection_options.use_property_decorate = False
        selection_options.separator()

        if len(file_data.bundles) > 0:
            if file_data.enable_multiselect:
                selection_options.prop(file_data, "proxy_enable_export")
                selection_options.separator()
                selection_options.prop(file_data, "proxy_export_location")
                selection_options.separator()
            else:
                entry = file_data.bundles[file_data.bundles_list_index]
                selection_options.prop(entry, "enable_export")
                selection_options.separator()
                selection_options.prop(entry, "export_location")
                selection_options.separator()
        
        selection_options.separator()
        # texture_ops = layout.column(align = True)
        # texture_ops.use_property_split = True
        # texture_ops.use_property_decorate = False
        selection_options.operator("pak.export_images", icon = 'EXPORT')
        # selection_box_area.separator()


class PAK_OT_Export(Operator):
    """Exports all images marked for export."""

    bl_idname = "pak.export_images"
    bl_label = "Export Selected"

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        report_info = {'exported_images': 0}
        export_time = datetime.now()

        # TODO: Add report info for images that weren't exported due to missing data.
        exportable = [[item for item in bundle.bundle_items 
                       if item.tex.PAK_Img.enable_export and item.tex.PAK_Img.export_location != '0']
                      for bundle in file_data.bundles]
        
        # TODO: Im sure this could be streamlined.
        exportable = set(i for j in exportable for i in j)
        exportable = [e for e in exportable]
        print(exportable)

        if len(exportable) == 0:
            self.report({'WARNING'}, "No exportable images found.  Make sure all images marked for export have a valid Export Location.")
            return {'FINISHED'}
        
        # TODO: Find a way to nicely merge verification with this iterator
        for bundle in file_data.bundles:
            for item in bundle.bundle_items:
                if item.tex.PAK_Img.enable_export and item.tex.PAK_Img.export_location != '0':
                    tex = item.tex
                    location_index = int(tex.PAK_Img.export_location) - 1
                    location = file_data.locations[location_index]

                    path = ReplacePathTags(location.path, True, bundle, export_time)
                    path = CreateFilePath(path)
                    
                    name = SubstituteNameCharacters(tex.name)

                    tex.save(filepath = path + name)
                    report_info['exported_images'] += 1
        
        if report_info['exported_images'] == 0:
            info = "PakPal exported no images."
            self.report({'WARNING'}, info)

        else:
            info = "PakPal successfully exported "

            if report_info['exported_images'] == 1:
                info += str(report_info['exported_images']) + ' image.'
            else:
                info += str(report_info['exported_images']) + ' images.'

            self.report({'INFO'}, info)
        

        return {'FINISHED'}

