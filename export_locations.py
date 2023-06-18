
import bpy, os, platform

from bpy.types import Menu, Panel, Operator, UIList
from bpy.props import EnumProperty


class PAK_OT_AddPath(Operator):
    """Create a new Export Location"""

    bl_idname = "scene.pak_addpath"
    bl_label = "Add"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pakpal_data_object].PAK_FileData
        except:
            return {'CANCELLED'}

        new_path = file_data.locations.add()
        new_path.name = "Location " + str(len(file_data.locations))
        new_path.path = ""

        return {'FINISHED'}
    

class PAK_OT_DeletePath(Operator):
    """
    Delete the selected export location from the list.  This will 
    also set the export location of all textures that used this to 'None'
    """

    bl_idname = "scene.pak_deletepath"
    bl_label = "Remove"

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pakpal_data_object].PAK_FileData
        except:
            return {'CANCELLED'}

        sel_index = file_data.locations_list_index

        # Ensure that any objects with a matching preset are set to None.
        # The index needs increasing by one as it doesnt include 'None'
        images = bpy.data.images
        for img in images:
            if img.PAK_Img.export_location == str(sel_index + 1):
                img.PAK_Img.export_location = '0'

        
        # TODO: Ensure the selection interface is updated so it gets the new value!
        # TODO: Ensure this is as efficient as it can be for large scenes
        
        # Once everything has been set, remove it.
        file_data.locations.remove(sel_index)

        # ensure the selected list index is within the list bounds
        if len(file_data.locations) > 0 and sel_index != 0:
            file_data.locations_list_index -= 1
        

        return {'FINISHED'}

class PAK_OT_AddExportLocTag(Operator):
    """Add a new export location tag to the currently selected location.  These are used to auto-name file structures with information about the export like file name, time, etc"""

    bl_idname = "scene.pak_add_export_loc_tag"
    bl_label = "Add Export Location Tag"

    path_tags: EnumProperty(
        name = "Add Path Tag",
        description = "",
        items =  (
        ('bundle_name', 'Bundle Name', 'Adds a folder with the name of the image bundle being exported (NOTE - The bundle must have more than one image)'),
        ('blend_file_name', 'Blend File Name', 'Adds a folder with the blend file name.'),
        ('export_date_ymd', 'Export Date (Year-Month-Day)', 'Adds a folder with the date of the export.'),
        ('export_date_dmy', 'Export Date (Day-Month-Year)', 'Adds a folder with the date of the export.'),
        ('export_date_mdy', 'Export Date (Month-Year-Day)', 'Adds a folder with the date of the export.'),
        ('export_time_hm', 'Export Time (Hour-Minute)', 'Adds a folder with the time of the export.'),
        ('export_time_hms', 'Export Time (Hour-Minute-Second)', 'Adds a folder with the time of the export.'),
        ),
    )

    def execute(self, context):

        try:
            addon_prefs = context.preferences.addons[__package__].preferences
            file_data = bpy.data.objects[addon_prefs.pakpal_data_object].PAK_FileData
        except:
            return {'CANCELLED'}
        
        # get the selected path
        path_index = file_data.locations_list_index
        new_path = file_data.locations[path_index].path
        end_path = ""

        # directory failsafe
        if platform.system() == 'Windows':
            if new_path.endswith("\\") == False and new_path.endswith("//") == False:
                new_path += "\\"
            end_path = "\\"
        else:
            if new_path.endswith("/") == False:
                new_path += "/"
            end_path = "\\"

        # insert the selected option into the currently selected path
        new_path += "^"
        new_path += self.path_tags
        new_path += "^" + end_path
        
        file_data.locations[path_index].path = new_path

        return {'FINISHED'}

class PAK_UL_ExportLocationList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        layout.prop(item, "name", text="", emboss=False)

class PAK_PT_Location(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Locations"
    bl_parent_id = "PROPERTIES_PT_Pak"
    bl_order = 2

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        try:
            file_data = bpy.data.objects[addon_prefs.pakpal_data_object].PAK_FileData
        except KeyError:
            return

        location_list = layout.row(align= True)
        location_list.template_list("PAK_UL_ExportLocationList", "default", file_data, 
                                   "locations", file_data, "locations_list_index", 
                                   rows = 3, maxrows = 6)
        location_list.separator()

        location_ops = location_list.column(align= True)
        location_ops.operator("scene.pak_addpath", text= "", icon = "ADD")
        location_ops.operator("scene.pak_deletepath", text= "", icon = "REMOVE")

        location_info = layout.column(align = False)
        location_info.use_property_split = True
        location_info.use_property_decorate = False
        location_info.separator()

        count = 0
        for i, item in enumerate(file_data.locations, 1):
            count += 1

        if file_data.locations_list_index > -1 and file_data.locations_list_index < count:
            location_info.prop(file_data.locations[file_data.locations_list_index], "path")
            # location_info.separator()
            location_info.operator_menu_enum("scene.pak_add_export_loc_tag", "path_tags")
            


def CreateFilePath(file_path, replace_invalid_chars = True):
    """
    Extracts and calculates a final path with which to export the target to.
    """


    if file_path == "":
        raise Exception('WARNING: This location preset has no path defined, please define it!')

    elif file_path.find('//') != -1:
        file_path = bpy.path.abspath(file_path)

    # If Windows, split the drive indicator
    drive_indicator = ""
    if platform.system() == 'Windows':
        drive_index = file_path.find("\\")

        if drive_index != -1:
            drive_split = file_path.split("\\", 1)
            drive_indicator = drive_split[0]
            file_path = drive_split[1]

    # directory failsafe
    if platform.system() == 'Windows':
        if file_path.endswith("\\") == False:
            file_path += "\\"
    else:
        if file_path.endswith("/") == False:
            file_path += "/"
    
    if replace_invalid_chars is True:
        file_path = SubstitutePathCharacters(file_path)

    # Windows drive indicator re-stitch
    if drive_indicator != "":
        file_path = drive_indicator + "\\" + file_path
    
    # Build the file path
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    return file_path

def SubstituteNameCharacters(path):
  # Replaces invalid directory characters in names

  result = path
  if platform.system() == 'Windows':
      invalid_characters = ["\\", "/", "*", "?", "\"", "<", ">", "|", ":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'Darwin':
      invalid_characters = [":", "/"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalid_characters = [":", "/"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  return result

def SubstitutePathCharacters(path):
  # Replaces invalid directory characters in full export paths

  result = path
  if platform.system() == 'Windows':
      invalid_characters = ["*", "?", "<", ">", "|", ":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'Darwin':
      invalid_characters = [":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  elif platform.system() == 'linux' or platform.system() == 'linux2':
      invalid_characters = [":"]
      for char in invalid_characters:
          result = result.replace(char, "_")

  return result

def ReplacePathTags(file_path, replace_invalid_chars, bundle, export_time):
    """
    Searches for and substitutes the tags in a path name.  USE THIS AFTER CreateFilePath().
    """


    if file_path.find('^bundle_name^'):

        bundle_name = ""
        if len(bundle.bundle_items) > 0:
            bundle_name = bundle.name

        if replace_invalid_chars is True:
            bundle_name = SubstituteNameCharacters(bundle_name)

        file_path = file_path.replace('^bundle_name^', bundle_name)

    
    if file_path.find('^blend_file_name^'):

        blend_name = bpy.path.basename(bpy.context.blend_data.filepath)
        blend_name = blend_name.replace(".blend", "")

        if replace_invalid_chars is True:
            blend_name = SubstituteNameCharacters(blend_name)

        file_path = file_path.replace('^blend_file_name^', blend_name)
    
    
    # DATE AND TIME

    if file_path.find('export_date_ymd'):
        
        time = export_time.strftime('%Y-%m-%d')
        file_path = file_path.replace('^export_date_ymd^', time)

    if file_path.find('export_date_dmy'):

        time = export_time.strftime('%d-%m-%Y')
        file_path = file_path.replace('^export_date_dmy^', time)

    if file_path.find('export_date_mdy'):

        time = export_time.strftime('%m-%d-%Y')
        file_path = file_path.replace('^export_date_mdy^', time)
    
    if file_path.find('export_time_hm'):

        time = export_time.strftime('%H.%M')
        file_path = file_path.replace('^export_time_hm^', time)

    if file_path.find('export_time_hms'):

        time = export_time.strftime('%H.%M.%S')
        file_path = file_path.replace('^export_time_hms^', time)
    
    return file_path    