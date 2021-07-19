
import os
import json

def get_base_path():
    path= os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(path,"settings.json")

def get_data():
    basePath = get_base_path()
    file_setting = open(basePath,'r')
    data = json.load(file_setting) 
    file_setting.close()
    return data

def get_baudrate():
    data = get_data()
    return data['preferences']['baud_rate']['value']

def get_port_name():
    data = get_data()
    return data['preferences']['serial_name']['value']

def get_camera_id():
    data = get_data()
    return data['preferences']['camera_id']['value']

def get_brightness():
    data = get_data()
    return data['capture']['brightness']

def get_contrast():
    data = get_data()
    return data['capture']['contrast']

def get_saturation():
    data = get_data()
    return data['capture']['saturation']

def get_exposure():
    data = get_data()
    return data['capture']['exposure']

def get_thresh():
    data = get_data()
    return data['capture']['thresh']

def get_max():
    data = get_data()
    return data['capture']['max']

def get_path_gcode():
    data = get_data()
    return data['gcode']['path']

def get_min():
    data = get_data()
    return data['capture']['min']

def get_size():
    data = get_data()
    return data['capture']['size']

def get_para_delta():
    data = get_data()
    return data['delta']

def get_capture():
    data = get_data()
    return data['capture']

def get_control_line():
    data = get_data()
    return data['control_line']

def get_scale():
    data = get_data()
    return data['scale']

def set_error_width(value):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['scale']['ew'] = value
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_error_height(value):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['scale']['eh'] = value
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_error_delay_motor(value):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['scale']['delay_motor'] = value
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_baudrate(value):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['preferences']['baud_rate']['value'] = value
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_portname(port_name):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['preferences']['serial_name']['value'] = port_name
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_camera_id(id_name):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['preferences']['camera_id']['value'] = id_name
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()

def set_para_delta(value):
    path = get_base_path()
    f = open(path, "r")
    data = json.load(f)
    data['delta'] = value
    f.close()
    f = open(path, "w")
    json.dump(data,f,ensure_ascii=False, indent=4)
    f.close()


if __name__=="__main__":
    print("error delay motor")
    set_error_delay_motor(0.025)