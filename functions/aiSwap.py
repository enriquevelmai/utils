import maya.cmds as mc
def ai_standard_material_to_lambert():
    for m in mc.ls(type="aiStandardSurface"):
        out_color_con = mc.listConnections(m + ".outColor", plugs=True)
        print out_color_con
        col = mc.getAttr(m + ".baseColor")[0]
        lam = mc.createNode("lambert")
        mc.setAttr(lam + ".color", *col)
        for con in out_color_con:
            mc.connectAttr(lam + ".outColor", con, f=True)
        mc.delete(m)
        mc.rename(lam, m)

ai_standard_material_to_lambert()