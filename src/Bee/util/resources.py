
import os

resource_base_path = ''

def set_base_path(path):
    global resource_base_path
    resource_base_path = path

def get_path_for_resource(directory, resource_name):
    assert os.path.isdir(resource_base_path), "{p} is not a directory".format(p=resource_base_path)
    path = os.path.normpath(os.path.join(resource_base_path, directory, resource_name))
    return path

def get_path_for_image(name):
    return get_path_for_resource('images', name)

def get_path_cv2(name):
    return get_path_for_resource('save', name)

def get_path_for_firmware(name):
    return get_path_for_resource('firmware', name)

def get_path_for_data(name):
    return get_path_for_resource('dataset', name)

def get_path_for_grbl(name):
    return get_path_for_resource('grbl', name)

def get_path_for_stl(name):
    return get_path_for_resource('stl', name)