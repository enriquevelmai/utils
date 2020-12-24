import maya.cmds as mc


def get_set(deformer):
    return mc.listConnections('{}.message'.format(deformer), source=True)[0]


def find_related_skincluster():
    raise NotImplementedError
