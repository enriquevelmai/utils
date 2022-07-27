import maya.cmds as mc
import maya.mel as mm


def text_to_curve(text, curve_name, size=10):
    # get maya text
    big_transform = mc.textCurves(n='Test', t=text, o=True)[0]

    # parent the shapes of the transforms into a new node
    tra = mc.createNode('transform', name=curve_name)
    all_curves_shape_list = [c for c in mc.listRelatives(big_transform, ad=True) if mc.objectType(c) == 'nurbsCurve']
    all_curves_transform_list = [mc.listRelatives(c, p=True)[0] for c in all_curves_shape_list]
    dupes = mc.duplicate(all_curves_transform_list)
    mc.parent(dupes, w=True)
    mc.makeIdentity(dupes, apply=True, t=True, r=True, s=True, n=False, pn=True)
    mc.delete(big_transform)
    for curve in dupes:
        mc.parent(mc.listRelatives(curve, c=True, s=True, fullPath=True)[0], tra, r=True, s=True)
    mc.delete(dupes)

    # rename shapes
    for i, shape in enumerate(mc.listRelatives(tra, s=True, fullPath=True)):
        new_name = mc.rename(shape, '{}Shape{}'.format(tra, str(i).zfill(2)))
        mc.setAttr(new_name + '.ihi', 0)

    # center pivot and place to (0,0,0)
    mc.xform(tra, cp=True)
    zero = mc.createNode('transform')
    mc.delete(mc.parentConstraint(zero, tra))
    mc.delete(zero)

    # add extra scale
    mc.xform(tra, s=(size / 10, size / 10, size / 10), r=True)
    mc.makeIdentity(tra, apply=True, s=True)

    return tra


def get_center_edge(geo):
    all_vertex = mc.ls('{}.vtx[*]'.format(geo), fl=True)
    choosed_vertex = list()
    for vtx in all_vertex:
        mc.select(vtx)
        mm.eval("PolySelectTraverse 1")
        selected_vertex = mc.ls(sl=True, fl=True)
        if len(selected_vertex) == 9:
            choosed_vertex.append(vtx)
        mc.select(d=True)
    mc.select(choosed_vertex)
    mm.eval("ConvertSelectionToContainedEdges")
    mm.eval("SelectContiguousEdges")
    center_edge = mc.ls(sl=True, fl=True)
    mc.select(d=True)
    return center_edge


def edge_to_curve(edge):
    mc.select(edge)
    mm.eval("polyToCurve -form 2 -degree 3 -conformToSmoothMeshPreview 1;")
    crv = mc.ls(sl=True)[0]
    real_name = mc.rename(crv, edge[0].split('.')[0].replace('GEO', 'CRV'))
    mc.select(d=True)
    return real_name
