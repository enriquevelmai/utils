import maya.cmds as mc


def create_blendshape_splitter_setup():
    # get base shape
    base_object = mc.ls(sl=True)[-1]

    # get target shapes
    target_objects = mc.ls(sl=True)[:-1]
    target_number = len(target_objects)

    # base bbox for base shape
    xmin, ymin, zmin, xmax, ymax, zmax = mc.exactWorldBoundingBox(base_object)
    height = (ymax - ymin)
    width = (xmax - xmin)

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
               defaultValue=width / 8.0,
               keyable=True)
    mc.addAttr(splitter_main_manager,
               longName="numberOfShapesPerRow",
               attributeType="long",
               defaultValue=target_number // 2,
               keyable=True,
               minValue=1)

    # create falloff primitives (settable and automatic)
    set_falloff = mc.createNode("primitiveFalloff", name="C_settable_FFO")
    auto_falloff = mc.createNode("primitiveFalloff", name="C_auto_FFO")
    mc.hide(auto_falloff)
    mc.setAttr(set_falloff + ".s", 1, height / 2.0, height / 2.0)
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

            # position automatism
            index_divide = mc.createNode("multiplyDivide", name=side + "_" + target_object + "IndexDivision_MDN")
            mc.setAttr(index_divide + ".operation", 2)
            mc.setAttr(index_divide + ".input1X", i)
            mc.connectAttr(splitter_main_manager + ".numberOfShapesPerRow", index_divide + ".input2X")

            integer_division = mc.createNode('animCurveUU', name=side + "_" + target_object + "IntegerDivision_AUU")
            mc.setKeyframe(integer_division, float=0, value=0, inTangentType="clamped", outTangentType="step")
            mc.setKeyframe(integer_division, float=1, value=1, inTangentType="clamped", outTangentType="step")
            mc.setAttr(integer_division + ".preInfinity", 4)
            mc.setAttr(integer_division + ".postInfinity", 4)
            mc.connectAttr(index_divide + ".outputX", integer_division + ".input")

            # ty
            height_mdl = mc.createNode("multDoubleLinear", name=side + "_" + target_object + "Height_MDL")
            mc.setAttr(height_mdl + ".input1", height)
            mc.connectAttr(integer_division + ".output", height_mdl + ".input2")

            # tx
            integer_recomposition_mdl = mc.createNode("multDoubleLinear", name=side + "_" + target_object + "Recom_MDL")
            mc.connectAttr(integer_division + ".output", integer_recomposition_mdl + ".input1")
            mc.connectAttr(splitter_main_manager + ".numberOfShapesPerRow", integer_recomposition_mdl + ".input2")
            residual_pma = mc.createNode("plusMinusAverage", name=side + "_" + target_object + "Residual_PMA")
            mc.setAttr(residual_pma + ".input1D[0]", i)
            mc.connectAttr(integer_recomposition_mdl + ".output", residual_pma + ".input1D[1]")
            mc.setAttr(residual_pma + ".operation", 2)
            width_mdl = mc.createNode("multDoubleLinear", name=side + "_" + target_object + "Width_MDL")
            mc.connectAttr(residual_pma + ".output1D", width_mdl + ".input1")
            mc.setAttr(width_mdl + ".input2", width)
            width_adl = mc.createNode("addDoubleLinear", name=side + "_" + target_object + "Width_ADL")
            mc.connectAttr(width_mdl + ".output", width_adl + ".input1")
            mc.setAttr(width_adl + ".input2", width)
            side_width_mdl = mc.createNode("multDoubleLinear", name=side + "_" + target_object + "Side_MDL")
            mc.connectAttr(width_adl + ".output", side_width_mdl + ".input1")
            mc.setAttr(side_width_mdl + ".input2", -1 if side == "R" else 1)

            # (width * (i % 2) + width) * (-1 if side == "R" else 1)
            mc.connectAttr(side_width_mdl + ".output", split_mesh + ".tx")
            # height * (i//2)
            mc.connectAttr(height_mdl + ".output", split_mesh + ".ty")

    # order is important
    for child in reversed(sorted(mc.listRelatives(split_meshes_grouper, children=True))):
        mc.reorder(child, front=True)


if __name__ == "__main__":
    create_blendshape_splitter_setup()
