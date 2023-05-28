import bpy

def PAK_Update_EnableExport(self, context):
    """
    Updates the "Enable Export" property for all selected images
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
    except KeyError:
        return
    
    value = file_data.proxy_enable_export

    if file_data.enable_multiselect:
        for tex in file_data.textures:
            if tex.is_selected:
                tex.tex.PAK_Tex.enable_export = value

    else:
        tex = file_data.textures[file_data.textures_list_index]
        tex.tex.PAK_Tex.enable_export = value

    return None

def PAK_Update_ExportLocation(self, context):
    """
    Updates the "Export Location" property for all selected images
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.default_datablock].PAK_FileData
    except KeyError:
        return
    
    value = file_data.proxy_export_location

    if file_data.enable_multiselect:
        for tex in file_data.textures:
            if tex.is_selected:
                tex.tex.PAK_Tex.export_location = value

    else:
        tex = file_data.textures[file_data.textures_list_index]
        tex.tex.PAK_Tex.export_location = value

    return None
