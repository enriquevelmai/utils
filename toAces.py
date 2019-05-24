import maya.cmds as mc

node_type = "file"
mapping_types = {"srgb": "Utility - sRGB - Texture",
                 "raw": "Utility - Raw"}

for node in mc.ls(type=node_type):
    origin_color_type = mc.getAttr("{}.colorSpace".format(node)).lower()
    if origin_color_type in mapping_types.keys():
        mc.setAttr("{}.colorSpace".format(node), mapping_types[origin_color_type], type="string")
        print('"{}" file has changed the color space from {} to {}'.format(node,
                                                                           origin_color_type,
                                                                           mapping_types[origin_color_type]))
