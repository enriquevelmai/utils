import maya.cmds as mc
import maya.mel as mm


def delete_unknown_nodes():
    unknownNodes = mc.ls(type="unknown")
    for item in unknownNodes:
        if mc.objExists(item):
            mc.delete(item)


def removed_unsused_influences(groups=None):
    if isinstance(groups, str):
        groups = [groups]

    for group in groups:
        for node in mc.listRelatives(group, allDescendents=True):
            if not mc.objectType(node) == 'mesh':
                continue
            print node
            node_transform = mc.listRelatives(node, p=True)[0]
            skin_node = [n for n in mc.listHistory(node_transform, pruneDagObjects=True) if mc.objectType(n)][0]
            if skin_node:
                if mc.objectType(skin_node) == 'skinCluster':
                    mc.select(node_transform)
                    mm.eval("removeUnusedInfluences;")


def delete_unused_nodes():
    mm.eval("MLdeleteUnused;")


def delete_turtle():
    turtle_node = "TurtleDefaultBakeLayer"
    if mc.objExists(turtle_node):
        mc.lockNode(turtle_node, lock=False)
        mc.delete(turtle_node)


def alphabet_reorder():
    # you have to select what you want to reorder
    lista = mc.ls(sl=True)
    lista.sort()
    lista.reverse()
    for n in lista:
        mc.reorder(n, front=True)
