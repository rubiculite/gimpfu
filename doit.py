#!/usr/bin/env python

import os
import re
import json

from gimpfu import *

# notes: 
# [0] https://www.gimp.org/docs/python/index.html
# [1] https://stackoverflow.com/questions/24626608/how-to-combine-several-png-images-as-layers-in-a-single-xcf-image
# [2] Running in batch mode:
#     - https://ntcore.com/?p=509
#     - https://stackoverflow.com/questions/44430081/how-to-run-python-scripts-using-gimpfu-from-windows-command-line
#     - https://www.gimp.org/tutorials/Basic_Batch/
#     In short, for gimp-2.10 on Mac OS X, do...
#
#        /Applications/GIMP-2.10.app/Contents/MacOS/gimp --no-interface --batch '(python-fu-do-it RUN-NONINTERACTIVE)' -b '(gimp-quit 1)' 
#


# maps channel string to channel gimp object
def map_string_to_channel(channel):
    if channel == "HISTOGRAM_VALUE":
        return HISTOGRAM_VALUE
    if channel == "HISTOGRAM_RED":
        return HISTOGRAM_RED
    if channel == "HISTOGRAM_GREEN":
        return HISTOGRAM_GREEN
    if channel == "HISTOGRAM_BLUE":
        return HISTOGRAM_BLUE
    return channel

# finds full directory path to source code
# NB: this is required, as the script is executed
#     via symbolic-link, and we need to know where
#     files are relative to the script. In short,
#     this allows for proper souce control, without
#     clogging up the plugin-directroy.
def get_this_source_file_directory():
    def path(fullpath):
        return re.sub(r"(.*/).*$",r"\1",fullpath)
    return path(os.path.realpath(__file__))

# gimfu invariant load -- won't bail
# NB: 'keys' are mapped to u'keys' as gimp prefers this.
def json_load():
    # load config file
    default_config_file = get_this_source_file_directory()+"config.json"
    config = json.load(open(default_config_file,'r'))

    # make sure masking parameters are within acceptable bounds
    if 'mask' in config:
        def normalize(mask):
             # clip mask if outside [0,500]
            if mask < 0:
                return 0.0
            if mask > 500:
                return 500.0
            return mask
        mask = config['mask']
        mask[u'horizonal_pixels'] = normalize(mask['horizonal_pixels'])
        mask[u'vertical_pixels'] = normalize(mask['vertical_pixels'])
        if 'opacity' in mask:
            # clip opacity if outside [0,100]
            opacity = float(mask['opacity'])
            if opacity < 0:
               opacity = 0.0
            elif opacity > 100:
               opacity = 100.0
        else:
            opacity = 100.0
        mask[u'opacity'] = opacity

    # assemble image paramaters
    for image in config['images']:
        image[u'file'] = config['path'] + image['file']
        image[u'layer'] = None # add layer key for loaded images
        if 'curves' in image:
            # add control points
            for curve in image['curves']:
                curve[u'control_points'] = [ordinate for cp in curve['control_points'] for ordinate in cp]
                curve[u'num_points'] = len(curve['control_points'])
                max_cp = float(max(curve['control_points']))
                if max_cp < 255.0:
                    max_cp = 255.0
                curve[u'control_points'] = [float(cp)/max_cp for cp in curve['control_points']]
    return config

# gimfu parameter dependent load
def load_config():
    # pre-filter config file
    config = json_load()

    # load image channel objects
    for image in config['images']:
        if 'levels' in image:
            for level in image['levels']:
                level[u'channel'] = map_string_to_channel(level['channel'])
        if 'curves' in image:
            for curve in image['curves']:
                curve[u'channel'] = map_string_to_channel(curve['channel'])
    return config

# hello workd plugin source code
def do_it():
    # load the config file
    config = load_config()
    has_mask = 'mask' in config

    # This procedure creates an image with the given dimensions and 
    # type (type is one of RGB , GRAY or INDEXED ).
    img = gimp.Image(1,1,RGB)

    # load images
    images = config['images']
    for image in images:
        image['layer'] = pdb.gimp_file_load_layer(img,image['file'])

    # set target img to image size
    width  = images[0]['layer'].width
    height = images[0]['layer'].height
    img.resize(width,height,0,0)

    # create background mage layer
    background = pdb.gimp_layer_new(img,width,height,RGB,"Background",100,LAYER_MODE_NORMAL)
    pdb.gimp_image_insert_layer(img,background,None,0)

    # insert image layers
    for image in images:
        pdb.gimp_layer_set_mode(image['layer'],LAYER_MODE_SCREEN)
        pdb.gimp_layer_set_name(image['layer'],image['label'])
        pdb.gimp_image_insert_layer(img,image['layer'],None,0)

    if has_mask:
        # make masking layer out of unmodified images...
        pdb.gimp_item_set_visible(background,False)
        mask = pdb.gimp_layer_new_from_visible(img,img,'Mask')
        pdb.gimp_layer_set_mode(mask,LAYER_MODE_OVERLAY)
        pdb.gimp_item_set_visible(background,True)

    # set the levels and curves
    for image in images:
       layer = image['layer']
       if 'levels' in image:
           for level in image['levels']:
               pdb.gimp_drawable_levels(
                   layer,
                   level['channel'],
                   level['low_input'],
                   level['high_input'],
                   level['clamp_input'],
                   level['gamma'],
                   level['low_output'],
                   level['high_output'],
                   level['clamp_output']
               )
       if 'curves' in image:
           for curve in image['curves']:
               pdb.gimp_drawable_curves_spline(
                   layer,
                   curve['channel'],
                   curve['num_points'],
                   curve['control_points']
               )

    # merge
    merged = pdb.gimp_layer_new_from_visible(img,img,'Merged')
    pdb.gimp_image_insert_layer(img,merged,None,0)
    for image in images:
        pdb.gimp_item_set_visible(image['layer'],False)
    pdb.gimp_item_set_visible(background,False)

    if has_mask:
        # do masking...
        masking = config['mask']
        pdb.gimp_image_insert_layer(img,mask,None,0)
        pdb.plug_in_gauss(
            #RUN_INTERACTIVE, # NB: don't include this: cf., iplug_in_gauss_rle
                              # at, https://www.gimp.org/docs/python/index.html
            img,              # (unused)
            mask,
            masking['horizonal_pixels'], # horizontal [0,500] pixels
            masking['vertical_pixels'],  # vertical [0,500] pixels
            0.5               # IIR(0) <= method <= RLE(1) (NB: ignored)
        )
        pdb.gimp_layer_set_opacity(mask,masking['opacity'])

        # create the final product...
        results = pdb.gimp_layer_new_from_visible(img,img,"Results")
        pdb.gimp_item_set_visible(merged,False)
        pdb.gimp_item_set_visible(mask,False)
        pdb.gimp_image_insert_layer(img,results,None,0)
    else:
        results = merged
    pdb.gimp_channel_set_name(results,"Et Voila!")

    # save the results
    output_dir = config["path"]+".tmp/"
    try:
        os.makedirs(output_dir)
    except:
        pass
    # notes: https://choboprogrammer.wordpress.com/2010/12/17/writing-python-script-for-gimp/
    output_png_file = output_dir+"results.png"
    pdb.file_png_save_defaults(
        #RUN_INTERACTIVE,
        img,
        results,
        output_png_file,
        output_png_file
    )

    try:
        # display as image
        gimp.Display(img)
    except:
        # non-interactive mode
        pass

    print "Done it!"

# plugin registration
register(
    "do-it",
    "Color workshop workflow experimental plugin.",
    "Color workshop workflow experimental plugin.",
    "Bart Simpson", "That Dam Dog Inc.","2050",
    "Do it!",
    "",
    [],
    [],
    # the function
    do_it,
    menu="<Image>/File/Create"
)

# start/install the plugin
main()
