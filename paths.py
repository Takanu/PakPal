import bpy, os, platform


def CreateFilePath(export_location, targets, replace_invalid_chars):
    """
    Extracts and calculates a final path with which to export the target to.
    """

    # First fetch the path
    location_path = export_location.path

    if location_path == "":
        raise Exception('WARNING: This location preset has no path defined, please define it!')

    elif location_path.find('//') != -1:
        location_path = bpy.path.abspath(location_path)

    # If Windows, split the drive indicator
    drive_indicator = ""
    if platform.system() == 'Windows':
        drive_index = location_path.find("\\")

        if drive_index != -1:
            drive_split = location_path.split("\\", 1)
            drive_indicator = drive_split[0]
            location_path = drive_split[1]
    

    #print("Current Location Path - ", location_path)

    # Now substitute any tags
    # location_path = FillTags(location_path, targets, collection, replace_invalid_chars, export_task)

    # directory failsafe
    if platform.system() == 'Windows':
        if location_path.endswith("\\") == False:
            location_path += "\\"
    else:
        if location_path.endswith("/") == False:
            location_path += "/"
    
    if replace_invalid_chars is True:
        location_path = SubstitutePathCharacters(location_path)

    # Windows drive indicator re-stitch
    if drive_indicator != "":
        location_path = drive_indicator + "\\" + location_path
    
    # Build the file path
    if not os.path.exists(location_path):
        os.makedirs(location_path)
    
    #print("Final Location Path - ", location_path)
    
    return location_path

def SubstituteNameCharacters(path):
  # Replaces invalid directory characters in names

  #print("Checking Directory...", path)
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

  #print("Checking Directory...", path)
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