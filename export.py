
import bpy, os, platform

from datetime import datetime
from bpy.types import Operator, Panel, UIList
from bpy.props import EnumProperty

from .main_menu import PAK_UI_CreatePakData, PAK_UI_CreateSelectionHeader
from .export_locations import CreateFilePath, SubstituteNameCharacters, ReplacePathTags
from .image_format_properties import LoadImageFormat, GetImageFileExtension

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

        selection_options = selection_box.column(align = True)
        selection_options.use_property_split = True
        selection_options.use_property_decorate = False
        selection_options.separator()

        if len(file_data.bundles) > 0:
            if file_data.enable_multiselect:
                selection_options.prop(file_data, "proxy_enable_export")
                selection_options.separator()
                selection_options.prop(file_data, "proxy_export_location")
                selection_options.separator()
                selection_options.prop(file_data, "proxy_export_format")
                selection_options.separator()
            else:
                entry = file_data.bundles[file_data.bundles_list_index]
                selection_options.prop(entry, "enable_export")
                selection_options.separator()
                selection_options.prop(entry, "export_location")
                selection_options.separator()
                selection_options.prop(entry, "export_format")
                selection_options.separator()
        
        selection_options.separator()
        # texture_ops = layout.column(align = True)
        # texture_ops.use_property_split = True
        # texture_ops.use_property_decorate = False
        selection_options.operator("pak.export_images", icon = 'EXPORT', text = 'Export Selected').set_mode = 'SELECTED'
        selection_options.operator("pak.export_images", icon = 'EXPORT', text = 'Export All Active').set_mode = 'ALL'
        # selection_box_area.separator()


class PAK_OT_Export(Operator):
    """Exports images marked for export"""

    bl_idname = "pak.export_images"
    bl_label = "Export"

    # This is important, pay attention :eyes:
    set_mode: EnumProperty(
        name = "Export Mode",
        items = [
            ('ALL', "All Active", "Exports all images in the Blend file that have been marked for export"),
            ('SELECTED', "Selected", "Exports the currently selected images.  This will include any images that HAVE NOT been marked for export"),
            ],
        default = 'ALL',
        description = "Execution mode", 
        options = {'HIDDEN'},
    )

    # Thanks!
    # https://blender.stackexchange.com/questions/19500/controling-compositor-by-python
    # https://docs.blender.org/api/current/bpy.types.CompositorNode.html
    def create_export_nodes(self):
        
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # BUILD IMAGE NODE
        input_node = tree.nodes.new(type = 'CompositorNodeImage')
        input_node.image = self.source_image
        input_node.location = 0,0

        # BUILD OUTPUT
        output_node = tree.nodes.new(type = 'CompositorNodeViewer')
        output_node.location = 300,0

        links.new(input_node.outputs[0], output_node.inputs[0])

        

    def execute(self, context):
        
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
        except:
            return {'CANCELLED'}

        report_info = {'exported_images': 0}
        export_time = datetime.now()

        if self.set_mode == "ALL":
            pass
        else:
            pass

        # /////////////////////////////////////////////////////////////////
        # FIND EXPORTABLE IMAGES

        # TODO: Add report info for images that weren't exported due to missing data.
        exportable = [[item for item in bundle.bundle_items 
                       if item.tex.PAK_Img.enable_export and item.tex.PAK_Img.export_location != '0']
                      for bundle in file_data.bundles]
        
        # TODO: Im sure this could be streamlined.
        exportable = set(i for j in exportable for i in j)
        exportable = [e for e in exportable]

        if len(exportable) == 0:
            self.report({'WARNING'}, "No exportable images found.  Make sure all images marked for export have a valid Export Location.")
            return {'FINISHED'}
        
        # /////////////////////////////////////////////////////////////////
        # BUILD SCENE AND COMPOSITOR
        
        # NOTE - The context won't actually change unless we escape the properties context.
        # Properties > Output has it's own scene context!
        # TODO: Potentially find a way to change the scene context for just the properties panel.
        old_type = context.area.type
        context.area.type = 'VIEW_3D'
        bpy.ops.scene.new(type = 'NEW')
        composite_scene = bpy.context.scene


        # TODO: Add custom color management settings
        # These will prevent color alteration.
        composite_scene.render.image_settings.color_management = 'FOLLOW_SCENE'
        composite_scene.view_settings.view_transform = 'Standard'
        composite_scene.view_settings.look = 'None'

        
        # /////////////////////////////////////////////////////////////////
        # ITERATE AND EXPORT TARGETS

        # TODO: Find a way to nicely merge verification with this iterator
        for bundle in file_data.bundles:
            for item in bundle.bundle_items:
                if item.tex.PAK_Img.enable_export and item.tex.PAK_Img.export_location != '0':
                    tex = item.tex
                    location_index = int(tex.PAK_Img.export_location) - 1
                    location = file_data.locations[location_index]

                    format_index = int(tex.PAK_Img.export_format) - 1
                    self.source_image = item.tex

                    path = ReplacePathTags(location.path, True, bundle, export_time)
                    path = CreateFilePath(path)
                    name = SubstituteNameCharacters(tex.name)

                    print(format_index)

                    if format_index != -1:
                        format = file_data.formats[format_index]
                        file_ext = GetImageFileExtension(format.file_format)

                        # TODO: Provide the right image to the right node instead of doing this every export.
                        self.create_export_nodes()

                        # This 'should' load the format associated with the image into the compositor.
                        LoadImageFormat(format, composite_scene.render.image_settings)

                        # This renders whatever is on the compositor.
                        # When using a File Output node it will forcefully add a frame number
                        # to the end, so we do this instead.
                        bpy.ops.render.render(animation=False, write_still=False, 
                                            use_viewport=False, layer="", scene="")
                        
                        # Store the output image in it's own buffer and datablock.
                        viewer = bpy.data.images['Viewer Node']

                        # use save_render to avoid the viewer node datablock from becoming a FILE type.
                        viewer.save_render(filepath = path + name + file_ext)


                    else:
                        tex.save(filepath = path + name)
                    

                    
                    report_info['exported_images'] += 1

        # TODO: Delete the saved image once it's been packed. (decided not to right now just in case)
        # TODO: Fully test info statements

        # ///////////////////////////////////////////////////////////////////////////
        # RESTORE SCENE
        # Delete the composite scene and change the area context back.
        bpy.data.scenes.remove(composite_scene, do_unlink = True)
        context.area.type = old_type
        
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

