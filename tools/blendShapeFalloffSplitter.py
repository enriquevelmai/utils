import maya.cmds as mc


def create_blendshape_splitter_setup(base_mesh, target_meshes):
    """ For each target two meshes are created left (L_) and (R_). The falloff of the split could be managed by a
     falloff attribute in the "C_mainManager_LOC" node. For organization proposes the number of shapes per row could
    also be managed in the "C_mainManager_LOC" node.

    IMPORTANT:
        - The base mesh and all target meshes MUST have the SAME vertex number and the SAME topology. This tool does not
        check if the meshes have same topology nor vertex number. It is an assumption that it is made. The blendshape
        creation will stop the execution of this code.
        - It uses maya 2022 nodes so it ONLY works in maya 2022

    :param: base_mesh (str): Name of the transform of the mesh to use as a base
    :param: target_meshes (list of str): Names of the transforms to use as the targets
    """
    # get number of targets
    target_number = len(target_meshes)

    # base bbox for base shape
    xmin, ymin, zmin, xmax, ymax, zmax = mc.exactWorldBoundingBox(base_mesh)
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
    set_falloff = mc.createNode("primitiveFalloff", name="C_settable_FFO", skipSelect=True)
    auto_falloff = mc.createNode("primitiveFalloff", name="C_auto_FFO", skipSelect=True)
    mc.hide(auto_falloff)
    mc.setAttr(set_falloff + ".s", 1, height / 2.0, height / 2.0)
    for attr in ("t", "r", "s"):
        for axis in ("x", "y", "z"):
            mc.setAttr(set_falloff + "." + attr + axis, lock=True, keyable=False, channelBox=False)

    auto_falloff_mdl = mc.createNode("multDoubleLinear", name="C_autoFalloff_MDL", skipSelect=True)
    mc.setAttr(set_falloff + ".primitive", 1)
    mc.setAttr(auto_falloff + ".primitive", 1)
    mc.connectAttr(splitter_main_manager + ".falloff", set_falloff + ".start")
    mc.connectAttr(splitter_main_manager + ".falloff", auto_falloff + ".end")
    mc.connectAttr(splitter_main_manager + ".falloff", auto_falloff_mdl + ".input1")
    mc.setAttr(auto_falloff_mdl + ".input2", -1)
    mc.connectAttr(auto_falloff_mdl + ".output", set_falloff + ".end")
    mc.connectAttr(auto_falloff_mdl + ".output", auto_falloff + ".start")

    # create two blendshape nodes for each target named with "L_" or "R_" in the beginning
    l_bls = mc.createNode("blendShape", name="L_splitter_BLS", skipSelect=True)
    r_bls = mc.createNode("blendShape", name="R_splitter_BLS", skipSelect=True)
    split_meshes_grouper = mc.createNode("transform", name="C_splitMeshes_TRN", skipSelect=True)
    for i, target_object in enumerate(target_meshes):
        for side, falloff_node, bls in zip(["L", "R"], [set_falloff, auto_falloff], [l_bls, r_bls]):
            mc.connectAttr(base_mesh + ".outMesh", bls + ".originalGeometry[" + str(i) + "]")
            mc.connectAttr(base_mesh + ".outMesh", bls + ".input[" + str(i) + "].inputGeometry")
            mc.connectAttr(
                target_object + ".outMesh",
                bls + ".inputTarget[{0}].inputTargetGroup[{0}].inputTargetItem[6000].inputGeomTarget".format(i))
            mc.setAttr(bls + ".weight[" + str(i) + "]", 1)
            mc.connectAttr(falloff_node + ".outputWeightFunction", bls + ".weightFunction[" + str(i) + "]")
            split_mesh = mc.polyPlane(name=side + "_" + target_object, constructionHistory=False)[0]
            mc.parent(split_mesh, split_meshes_grouper)
            mc.connectAttr(bls + ".outputGeometry[" + str(i) + "]", split_mesh + ".inMesh")

            # position automatism
            index_divide = mc.createNode(
                "multiplyDivide", name=side + "_" + target_object + "IndexDivision_MDN", skipSelect=True)
            mc.setAttr(index_divide + ".operation", 2)
            mc.setAttr(index_divide + ".input1X", i)
            mc.connectAttr(splitter_main_manager + ".numberOfShapesPerRow", index_divide + ".input2X")

            integer_division = mc.createNode(
                'animCurveUU', name=side + "_" + target_object + "IntegerDivision_AUU", skipSelect=True)
            mc.setKeyframe(integer_division, float=0, value=0, inTangentType="clamped", outTangentType="step")
            mc.setKeyframe(integer_division, float=1, value=1, inTangentType="clamped", outTangentType="step")
            mc.setAttr(integer_division + ".preInfinity", 4)
            mc.setAttr(integer_division + ".postInfinity", 4)
            mc.connectAttr(index_divide + ".outputX", integer_division + ".input")

            # ty
            height_mdl = mc.createNode(
                "multDoubleLinear", name=side + "_" + target_object + "Height_MDL", skipSelect=True)
            mc.setAttr(height_mdl + ".input1", height)
            mc.connectAttr(integer_division + ".output", height_mdl + ".input2")

            # tx
            integer_recomposition_mdl = mc.createNode(
                "multDoubleLinear", name=side + "_" + target_object + "Recom_MDL", skipSelect=True)
            mc.connectAttr(integer_division + ".output", integer_recomposition_mdl + ".input1")
            mc.connectAttr(splitter_main_manager + ".numberOfShapesPerRow", integer_recomposition_mdl + ".input2")
            residual_pma = mc.createNode(
                "plusMinusAverage", name=side + "_" + target_object + "Residual_PMA", skipSelect=True)
            mc.setAttr(residual_pma + ".input1D[0]", i)
            mc.connectAttr(integer_recomposition_mdl + ".output", residual_pma + ".input1D[1]")
            mc.setAttr(residual_pma + ".operation", 2)
            width_mdl = mc.createNode(
                "multDoubleLinear", name=side + "_" + target_object + "Width_MDL", skipSelect=True)
            mc.connectAttr(residual_pma + ".output1D", width_mdl + ".input1")
            mc.setAttr(width_mdl + ".input2", width)
            width_adl = mc.createNode(
                "addDoubleLinear", name=side + "_" + target_object + "Width_ADL", skipSelect=True)
            mc.connectAttr(width_mdl + ".output", width_adl + ".input1")
            mc.setAttr(width_adl + ".input2", width)
            side_width_mdl = mc.createNode(
                "multDoubleLinear", name=side + "_" + target_object + "Side_MDL", skipSelect=True)
            mc.connectAttr(width_adl + ".output", side_width_mdl + ".input1")
            mc.setAttr(side_width_mdl + ".input2", -1 if side == "R" else 1)

            # (width * (i % 2) + width) * (-1 if side == "R" else 1)
            mc.connectAttr(side_width_mdl + ".output", split_mesh + ".tx")
            # height * (i//2)
            mc.connectAttr(height_mdl + ".output", split_mesh + ".ty")

    # order is important
    for child in reversed(sorted(mc.listRelatives(split_meshes_grouper, children=True))):
        mc.reorder(child, front=True)

    mc.select(splitter_main_manager)


if __name__ == "__main__":
    create_blendshape_splitter_setup(base_mesh=mc.ls(sl=True)[-1], target_meshes=mc.ls(sl=True)[:-1])
