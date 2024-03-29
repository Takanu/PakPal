
import bpy, os
from .material_slots import FindMaterialSlotInName
from .main_menu import CreatePakPreviewTexture

def PAK_Update_RefreshList(self, context):
    """
    Triggers an update of the Texture List
    """

    bpy.ops.pak.refresh_images()
    
    return

def PAK_Update_EnableExport(self, context):
    """
    Updates the "Enable Export" property for all selected images
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return
    
    if file_data.is_internal_update:
        return
    
    value = file_data.proxy_enable_export

    if file_data.enable_multiselect:
        for bundle in file_data.bundles:
            if bundle.is_selected:
                bundle.enable_export = value

    else:
        bundle = file_data.bundles[file_data.bundles_list_index].pak_items
        for tex in bundle:
            tex.PAK_Img.enable_export = value

    return None

def PAK_Update_ExportLocation(self, context):
    """
    Updates the "Export Location" property for all selected images
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return
    
    if file_data.is_internal_update:
        return
    
    value = file_data.proxy_export_location

    if file_data.enable_multiselect:
        for bundle in file_data.bundles:
            if bundle.is_selected:
                bundle.export_location = value

    else:
        bundle = file_data.bundles[file_data.bundles_list_index].pak_items
        for tex in bundle:
            tex.PAK_Img.export_location = value

    return None

def PAK_Update_ExportFormat(self, context):
    """
    Updates the "Export Format" property for all selected images
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return
    
    if file_data.is_internal_update:
        return
    
    value = file_data.proxy_export_format

    if file_data.enable_multiselect:
        for bundle in file_data.bundles:
            if bundle.is_selected:
                bundle.export_format = value

    else:
        bundle = file_data.bundles[file_data.bundles_list_index].pak_items
        for tex in bundle:
            tex.PAK_Img.export_format = value

    return None

def PAK_Update_EnableBundles(self, context):
    """
    Automatically refreshes the list when the Enable Bundles is toggled 
    in order to provide the right data.
    """

    bpy.ops.pak.refresh_images()



def PAK_Update_TextureListItem_Name(self, context):
    """
    Updates the name of a texture bundle from the list UI.
    """

    # self in this context is the bundle being interacted with

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return
    
    if file_data.is_internal_update:
        return
    
    value = self.name

    if file_data.enable_bundles is not True:
        for bundle_item in self.pak_items:
            bundle_item.tex.name = value
    
    else:
        for bundle_item in self.pak_items:
            tex = bundle_item.tex

            name_parts = [n for n in os.path.splitext(tex.name)]
            filename = name_parts.pop(0)
            extension = ""

            for text in name_parts:
                extension += text

            match = FindMaterialSlotInName(addon_prefs, filename, None,
                                           file_data.case_sensitive_matching)
            if match is not None:
                new_name = value + match + extension
                tex.name = new_name
            else:
                tex.name = value



def PAK_Update_TextureListItem_EnableExport(self, context):
    """
    Updates the Enable Export property of a texture bundle from the list UI.
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return

    if file_data.is_internal_update:
        return
    
    value = self.enable_export

    for bundle_item in self.pak_items:
        bundle_item.tex.PAK_Img.enable_export = value
        

def PAK_Update_TextureListItem_ExportLocation(self, context):
    """
    Updates the Export Location property of a texture bundle from the list UI.
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return

    if file_data.is_internal_update:
        return
    
    
    value = self.export_location

    for bundle_item in self.pak_items:
        bundle_item.tex.PAK_Img.export_location = value

def PAK_Update_TextureListItem_ExportFormat(self, context):
    """
    Updates the Export Format property of a texture bundle from the list UI.
    """

    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return

    if file_data.is_internal_update:
        return
    
    
    value = self.export_format

    for bundle_item in self.pak_items:
        bundle_item.tex.PAK_Img.export_format = value

def PAK_Update_TextureListItem_IsSelected(self, context):
    """
    Used to reset proxy export properties in the UI every time UI selection changes.
    """
    try:
        addon_prefs = context.preferences.addons[__package__].preferences
        file_data = bpy.data.objects[addon_prefs.pak_filedata_name].PAK_FileData
    except KeyError:
        return
    
    file_data.is_internal_update = True

    file_data.proxy_enable_export = False
    file_data.proxy_export_location = '0'
    
    file_data.is_internal_update = False


def PAK_Update_TextureList_Preview(self, context):
    """
    Updates the texture preview when the selection is changed.
    """

    # If the list has no entries, the preview texture shouldn't have anything in it.
    if len(self.bundles) == 0:
        if self.preview_tex != None:
            self.preview_tex.image = None
        else:
            self.preview_tex = None
        return
    
    sel_bundle = self.bundles[self.bundles_list_index]
    sel_texture = sel_bundle.pak_items[0].tex

    if self.preview_tex is None:
        CreatePakPreviewTexture()
        
    self.preview_tex.image = sel_bundle.pak_items[0].tex

    pass

def PAK_Update_TextureList_PreviewColor(self, context):

    sel_bundle = self.bundles[self.bundles_list_index]
    sel_texture = sel_bundle.pak_items[0].tex
    preview_rgb = self.preview_rgb

    if self.preview_tex is None:
        return

    if 'R' in preview_rgb:
        self.preview_tex.factor_red = 1
    else:
        self.preview_tex.factor_red = 0
    if 'G' in preview_rgb:
        self.preview_tex.factor_green = 1
    else:
        self.preview_tex.factor_green = 0
    if 'B' in preview_rgb:
        self.preview_tex.factor_blue = 1
    else:
        self.preview_tex.factor_blue = 0