"""
MIT License

Copyright (c) 2019 Enrique Velasco Mairal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import maya.cmds as mc

# define node type, by default it's file
node_type = "file"

# define mapping dict,
# "key" represents the previous color space ,non aces
# "value" represents de post color space, aces
mapping_types = {"srgb": "Utility - sRGB - Texture",
                 "raw": "Utility - Raw"}

for node in mc.ls(type=node_type):
    origin_color_type = mc.getAttr("{}.colorSpace".format(node)).lower()
    if origin_color_type in mapping_types.keys():
        mc.setAttr("{}.colorSpace".format(node), mapping_types[origin_color_type], type="string")
        print('"{}" file has changed the color space from "{}" to "{}"'.format(node,
                                                                               origin_color_type,
                                                                               mapping_types[origin_color_type]))
