#!/usr/bin/env python

# This is hello world plugin-in using gimpfu, a python interface package [1-3].
# [1] A good primer on python-plugins: https://www.gimp.org/docs/python/index.html
#     NB: Example code on-line are extremely GIMP version dependent; this script uses
#     GIMP-2.10. But not to worry, you can lookup the correct syntax by searching
#     through GIMP's procedure browser (Help -> Procedure Bowser), and adjust the examples
#     accordingly.
# [2] Mac OS X Notes:
#     a) Installing.
#        To run this on make Mac OS X, place this script_name.py in
#            /Users/<USERNAME>/Library/Application Support/GIMP/2.10/plug-ins
#        and make it executable (i.e., chmod 755 it).
#     b)  Debugging.
#        To debug start gimp on the command line, i.e.,
#            $ /Applications/GIMP-2.10.app/Contents/MacOS/gimp --verbose --console-messages
#        assuming you did a standard GIMP install.
#     c) Executing.
#        In GIMP do,
#            File -> Create -> "Hello world..."
#     d) Notes on Mac OS X and other platforms.
#           https://en.wikibooks.org/wiki/GIMP/Installing_Plugins
# [3] Cheat Sheet: http://gimpbook.com/scripting/
#

from gimpfu import *

# hello world plugin source code
def hello_world(initstr,font,size,color):
    img = gimp.Image(1,1,RGB)
    gimp.set_foreground(color)
    # note: this is a gimp procedure-database (pdb) function, as in, you can use the 
    #       procedure browser in gimp to get its definition information.
    layer = pdb.gimp_text_fontname(img,None,0,0,initstr,10,True,size,PIXELS,font)
    img.resize(layer.width, layer.height, 0, 0)
    # print to the console
    print "HELLO WORLD!"
    # display as image
    gimp.Display(img)

# plugin registration
register(
    # unique plugin name
    "python_fu_hello_world",
    # brief description.
    "Hello world image",
    # detail description
    "Create an image iwth a user-provided string",
    # author, copyright, date
    "Bart Simpson", "That Dam Dog Inc.","2050",
    # pulldown menu label
    "Hello world...",
    "",
    # parameter-template for diaglogue box mapping to function arguments.
    [
        (PF_STRING, "string", "String", 'Hello, world!'),
        (PF_FONT, "font", "Font face", "Sans"),
        (PF_SPINNER, "size", "Font size", 50, (1,3000,1)),
        (PF_COLOR, "color", "Text color",(1.0,0.5,0.0))
    ],
    [],
    # the function
    hello_world,
    # pulldown menu location
    menu="<Image>/File/Create"
)

# start/install the plugin
main()
