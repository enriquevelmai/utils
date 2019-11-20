import maya.cmds as mc


def copy():
    obj_selected = mc.ls(sl=True)
    origin_object = obj_selected[0]
    target_objects = obj_selected[1:]
    history = mc.listHistory(origin_object, pdo=True)
    skin_cluster_node = None
    for n in history:
        if mc.objectType(n) == 'skinCluster':
            skin_cluster_node = n

    influences = mc.skinCluster(skin_cluster_node, query=True, influence=True)

    for target_object in target_objects:
        mc.delete(target_object, constructionHistory=True)
        mc.skinCluster(influences, target_object, toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1)

        mc.copySkinWeights(origin_object, target_object, noMirror=True, surfaceAssociation='closestPoint',
                           influenceAssociation=['label', 'oneToOne'])


#################################
# USAGE !
#
# copy()
#################################