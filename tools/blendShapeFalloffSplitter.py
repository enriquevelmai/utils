import maya.cmds as mc


def create_blendshape_splitter_setup():
    # get base shape
    base_object = mc.ls(sl=True)[-1]

    # get target shapes
    target_objects = mc.ls(sl=True)[:-1]
    target_number = len(target_objects)

    # base bbox for base shape
    xmin, ymin, zmin, xmax, ymax, zmax = mc.exactWorldBoundingBox(base_object)
    height = ymax - ymin / 2.0
    width = xmax - xmin / 2.0

    # create main manager locator
    splitter_main_manager = mc.spaceLocator(name="C_mainManager_LOC")[0]
    mc.setAttr(splitter_main_manager + ".s", height, height, height)
    mc.xform(splitter_main_manager, t=(0, ymax * 1.2, 0), worldSpace=True)
    for attr in ("t", "r", "s"):
        for axis in ("x", "y", "z"):
            mc.setAttr(splitter_main_manager + "." + attr + axis, lock=True, keyable=False, channelBox=False)

    # add manager attributes
    mc.addAttr(splitter_main_manager,
               longName="falloff",
               attributeType="float",
               defaultValue=xmax / 3.0,
               keyable=True)
    mc.addAttr(splitter_main_manager,
               longName="numberOfShapesPerRow",
               attributeType="double",
               defaultValue=target_number / 2.0,
               keyable=True)

    # create falloff primitives (settable and automatic)
    set_falloff = mc.createNode("primitiveFalloff", name="C_settable_FFO")
    auto_falloff = mc.createNode("primitiveFalloff", name="C_auto_FFO")
    mc.hide(auto_falloff)
    mc.setAttr(set_falloff + ".s", 1, height, height)
    for attr in ("t", "r", "s"):
        for axis in ("x", "y", "z"):
            mc.setAttr(set_falloff + "." + attr + axis, lock=True, keyable=False, channelBox=False)

    auto_falloff_mdl = mc.createNode("multDoubleLinear", name="C_autoFalloff_MDL")
    mc.setAttr(set_falloff + ".primitive", 1)
    mc.setAttr(auto_falloff + ".primitive", 1)
    mc.connectAttr(splitter_main_manager + ".falloff", set_falloff + ".start")
    mc.connectAttr(splitter_main_manager + ".falloff", auto_falloff + ".end")
    mc.connectAttr(splitter_main_manager + ".falloff", auto_falloff_mdl + ".input1")
    mc.setAttr(auto_falloff_mdl + ".input2", -1)
    mc.connectAttr(auto_falloff_mdl + ".output", set_falloff + ".end")
    mc.connectAttr(auto_falloff_mdl + ".output", auto_falloff + ".start")

    # create two blendshape nodes for each target named with "L_" or "R_" in the beginning
    l_bls = mc.createNode("blendShape", name="L_splitter_BLS")
    r_bls = mc.createNode("blendShape", name="R_splitter_BLS")
    split_meshes_grouper = mc.createNode("transform", name="C_splitMeshes_TRN")
    for i, target_object in enumerate(target_objects):
        for side, falloff_node, bls in zip(["L", "R"], [set_falloff, auto_falloff], [l_bls, r_bls]):
            mc.connectAttr(base_object + ".outMesh", bls + ".originalGeometry[" + str(i) + "]")
            mc.connectAttr(base_object + ".outMesh", bls + ".input[" + str(i) + "].inputGeometry")
            mc.connectAttr(
                target_object + ".outMesh",
                bls + ".inputTarget[{0}].inputTargetGroup[{0}].inputTargetItem[6000].inputGeomTarget".format(i))
            mc.setAttr(bls + ".weight[" + str(i) + "]", 1)
            mc.connectAttr(falloff_node + ".outputWeightFunction", bls + ".weightFunction[" + str(i) + "]")
            split_mesh = mc.polyPlane(name=side + "_" + target_object, constructionHistory=False)[0]
            mc.parent(split_mesh, split_meshes_grouper)
            mc.connectAttr(bls + ".outputGeometry[" + str(i) + "]", split_mesh + ".inMesh")
            mc.xform(split_mesh, t=(width * (i + 1) * (-1 if side == "R" else 1), 0, 0), worldSpace=True)

    # order is important
    for child in reversed(sorted(mc.listRelatives(split_meshes_grouper, children=True))):
        mc.reorder(child, front=True)


if __name__ == "__main__":
    create_blendshape_splitter_setup()
