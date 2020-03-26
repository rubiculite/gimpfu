# GIMP-FU -- HiYaaa!

This directory contains python-gimp experimental tools.

## Hello World!

To get started, you'll find a highly annotated hello world example in the `hello_world_example` directory.

## Prototype Automation Script

Here, `doit.py` is a script for automatically stitching together radio images (in the `imgs` directory) and colorizing them. This script runs off of a `config.json` file located in the same directory, which contains setings for images paths,
```
{"path": "/Users/susy/workbench/gimpfu/imgs/",
   ...
}
```
image processing parameters,
```
       ...
    "images": [
    {"file": "ver1-4C48GHz2.22.jpg",
     "label": "2.22 GHz",
     "levels": [
         {"channel": "HISTOGRAM_RED",
          "low_input": 0,
          "high_input": 1,
          "clamp_input": false,
          "gamma": 1.0,
          "low_output": 0,
          "high_output": 0,
          "clamp_output": false},
         {"channel": "HISTOGRAM_GREEN",
          "low_input": 0,
          "high_input": 1,
          "clamp_input": false,
          "gamma": 1.0,
          "low_output": 0,
          "high_output": 0,
          "clamp_output": false}
     ],
     "curves": [
        {"channel": "HISTOGRAM_VALUE",
         "control_points": [[0,0],[80,15],[94,97],[137,220],[180,255],[222,236],[255,191]]
        }
     ]},
        ...
 ]
   ...
```
and masking,
```
   ...
 "mask": {
    "horizonal_pixels": 50.0,
    "vertical_pixels": 50.0,
    "opacity": 75
  },
   ...
```
To get started you'll need to change the `path` in `config.json` to point to the `imgs` diretory (*i.e.*, relabel, *`"path": "/Users/susy/workbench/gimpfu/imgs/",`* accordingly), and then create a symbolic link in GIMP's plug-ins directory: *e.g.*, on Mac OS X it's,
```
/Users/susy/Library/Application\ Support/GIMP/2.10/plug-ins
```
where `susy` is the username, so ...
```
$ cd /Users/susy/Library/Application\ Support/GIMP/2.10/plug-ins
$ ln -s /Users/susy/workbench/gimpfu/doit.py doit.py
$ ls -al
total 0
drwxr-xr-x   3 susy  staff    96  6 Feb 19:28 .
drwxr-xr-x  48 susy  staff  1536  6 Feb 19:29 ..
lrwxr-xr-x   1 susy  staff    58  6 Feb 19:28 doit.py -> /Users/susy/workbench/gimpfu/doit.py
$
```
and you're good to go!

By lauching GIMP and selecting `File -> Create -> Do it!` the script will run, display the resutls, and save the final images as, for example, `/Users/susy/cirada/Visualization/gimpfu/imgs/.tmp/results.png`. GIMP can also be launch from the command line for debugging purposes: *i.e.*, by entering,
```
$ /Applications/GIMP-2.10.app/Contents/MacOS/gimp --verbose --console-messages
```
while in the plugg-ins directory (*i.e.*, `/Users/susy/Library/Application Support/GIMP/2.10/plug-ins`).

One can also run the script in batch-mode, without the user interface: *i.e.*,
```
/Applications/GIMP-2.10.app/Contents/MacOS/gimp --no-interface --batch '(python-fu-do-it RUN-NONINTERACTIVE)' -b '(gimp-quit 1)'
```


