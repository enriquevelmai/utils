import maya.cmds as mc
import maya.mel as mm

for f in mc.ls(type="file"):
    mm.eval("generateUvTilePreview {}".format(f))
