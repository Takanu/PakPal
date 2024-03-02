
import bpy, os, platform

from datetime import datetime
from bpy.types import Operator, Panel, UIList
from bpy.props import EnumProperty

from .main_menu import PAK_UI_CreatePakData, PAK_UI_CreateSelectionHeader
from .export_locations import CreateFilePath, SubstituteNameCharacters, ReplacePathTags
from .image_format_properties import LoadImageFormat, GetImageFileExtension
from .operators import GetSelection

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
        selection_options.operator("pak.export_images", icon = 'EXPORT', text = 'Export All').set_mode = 'ALL'
        selection_options.operator("pak.export_images", icon = 'EXPORT', text = 'Export Selected').set_mode = 'SELECTED'
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
            # ('CAPSULE_SELECTED', "Capsule Selected", "This exports all images associated with an object selection.")
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

        report_info = {'exported_images': 0, 'no_export_location': 0}
        export_time = datetime.now()
        

        # /////////////////////////////////////////////////////////////////
        # FIND EXPORTABLE IMAGES
        # Because of bundles we have to separate the export options from the PAK
        # image data.

        # NOTE NOTE: Make sure you don't include hidden images unless enabled.
        exportable = []
        selected_bundles = []

        # Figure out candidates
        if self.set_mode == "ALL":
            selected_bundles = [bundle for bundle in file_data.bundles]

        else:
            selected_bundles = GetSelection(file_data)

        # Filter based on eligibility
        for bundle in selected_bundles:

            if (file_data.enable_bundles == True
                and bundle.enable_export == False):
                continue

            for item in bundle.pak_items:
                image = item.tex
                pak_data = None

                if file_data.enable_bundles == True:
                    pak_data = bundle
                else:
                    pak_data = item.tex.PAK_Img
                    
                if (pak_data.enable_export == False):
                    continue
                
                if pak_data.export_location == '0':
                    report_info['no_export_location'] += 1
                    continue

                export_target = {}
                export_target['image'] = image
                export_target['export_location'] = pak_data.export_location
                export_target['export_format'] = pak_data.export_format

                exportable.append(export_target)


        print(selected_bundles)
        print(exportable)

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
        composite_scene.render.image_settings.color_management = 'OVERRIDE'
        composite_scene.view_settings.view_transform = 'Standard'
        composite_scene.view_settings.look = 'None'

        
        # /////////////////////////////////////////////////////////////////
        # ITERATE AND EXPORT TARGETS

        for export_item in exportable:
            image = export_item['image']

            location_index = int(export_item['export_location']) - 1
            location = file_data.locations[location_index]

            format_index = int(export_item['export_format']) - 1
            self.source_image = image

            # TODO: Add file tag support
            # path = ReplacePathTags(location.path, True, bundle, export_time)
            path = CreateFilePath(location.path)
            filename = SubstituteNameCharacters(image.name)
            filename = filename.rsplit( ".", 1 )[ 0 ]

            if format_index != -1:
                format = file_data.formats[format_index]
                file_ext = GetImageFileExtension(format.file_format)
                filename = filename + file_ext

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
                viewer.save_render(filepath = path + filename)


            else:
                file_ext = GetImageFileExtension(image.file_format)
                filename = filename + file_ext
                image.save(filepath = path + filename)
            
            report_info['exported_images'] += 1
            
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

            if report_info['no_export_location'] > 0:
                info += "  " + str(report_info['no_export_location'])
                
                if report_info['no_export_location'] == 1:
                    info += ' image '
                else:
                    info += ' images '
                
                info += 'have no Export Location set.'
            
            self.report({'INFO'}, info)
        

        return {'FINISHED'}

