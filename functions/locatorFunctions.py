import maya.cmds as mc


def follow_locators_from_curve(curve_name):
    for cv in mc.ls("{}.cv[*]".format(curve_name), fl=True):
        cv_position = mc.xform(cv, q=True, ws=True, t=True)

        # get uv val
        npc = mc.createNode("nearestPointOnCurve")
        mc.connectAttr("{}.worldSpace[0]".format(curve_name), "{}.inputCurve".format(npc))
        mc.setAttr("{}.inPosition".format(npc), cv_position[0], cv_position[1], cv_position[2])
        parameter = mc.getAttr("{}.parameter".format(npc))
        mc.delete(npc)

        # set locator in position
        loc_shape = mc.createNode("locator")
        loc_trn = mc.listRelatives(loc_shape, p=True)[0]
        pci = mc.createNode("pointOnCurveInfo")
        mc.connectAttr("{}.worldSpace[0]".format(curve_name), "{}.inputCurve".format(pci))
        mc.setAttr("{}.parameter".format(pci), parameter)
        mc.connectAttr("{}.position".format(pci), "{}.translate".format(loc_trn))


def place_at_object(slave, target):
    matrix = mc.getAttr(target + '.worldMatrix')
    mc.xform(slave, m=matrix, ws=True)


def mesh_independent_rivets():
    raise NotImplementedError