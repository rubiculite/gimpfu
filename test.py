import re
import os
import yaml
import json

def get_this_source_file_directory():
    def path(fullpath):
        return re.sub(r"(.*/).*$",r"\1",fullpath)
    return path(os.path.realpath(__file__))

def yaml_load():
    default_config_file = get_this_source_file_directory()+"config.yml"
    config = yaml.load(open(default_config_file,'r'))
    for image in config['images']:
        image['file'] = config['path'] + image['file']
        image['layer'] = None
    return config

def json_load():
    default_config_file = get_this_source_file_directory()+"config.json"
    config = json.load(open(default_config_file,'r'))
    if 'mask' in config:
        def normalize(mask):
            if mask < 0:
                return 0.0
            if mask > 500:
                return 500.0
            return mask
        mask = config['mask']
        mask[u'horizonal_pixels'] = normalize(mask['horizonal_pixels'])
        mask[u'vertical_pixels'] = normalize(mask['vertical_pixels'])
        if 'opacity' in mask:
            opacity = float(mask['opacity'])
            if opacity < 0:
               opacity = 0.0
            elif opacity > 100:
               opacity = 100.0
        else:
            opacity = 100.0
        mask[u'opacity'] = opacity
    for image in config['images']:
        image[u'file'] = config['path'] + image['file']
        image[u'layer'] = None
        if 'curves' in image:
            for curve in image['curves']:
                curve[u'control_points'] = [ordinate for cp in curve['control_points'] for ordinate in cp]
                curve[u'num_points'] = len(curve['control_points'])
                max_cp = float(max(curve['control_points']))
                if max_cp < 255.0:
                    max_cp = 255.0
                curve[u'control_points'] = [float(cp)/max_cp for cp in curve['control_points']]
    return config

if __name__ == '__main__':
    print "PATH:",get_this_source_file_directory()
    print "YAML_CONFIG:\n",yaml.dump(yaml_load())
    print "JSON_CONFIG:\n",json.dumps(json_load(),indent=2,sort_keys=True)
    #print "JSON_CONFIG:\n",json_load()
