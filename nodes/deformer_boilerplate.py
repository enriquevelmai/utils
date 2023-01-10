import sys

# as deformers cannot be writen in Maya Python API 2.0 we will keep our code pure in API 1.0 due to the fact that
# their objects are not compatible. This will allow us to have an easier port to C++ code once the deformer prototype
# is finished
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import maya.cmds as mc


# Class definition
class MyDefomer(ommpx.MPxDeformerNode):
    # Node definition
    VENDOR = 'Kike'
    VERSION = '1.0'
    NODENAME = 'theDeformer'
    NODEID = om.MTypeId(0x00118383)

    def __init__(self):
        super(MyDefomer, self).__init__()

    def deform(self, data_block, geo_iter, matrix, multi_index):
        """
        Compute when evaluating the node, we can modify the specific components of the geometry.
        :param data_block: (om.MDataBlock): Access to the deformer attributes
        :param geo_iter: (om.MItGeometry):  in order to move for the cvs or vertices of the geometry
        :param matrix: (om.MMatrix): as the components in the geo_iter are in local space, this matrix allows adding the object
        global transformations
        :param multi_index: (int): index of the corresponding requested output geometry
        :return:
        """
        # example to access attributes
        envelope = data_block.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return

        # example to iterate the geometry
        geo_iter.reset()
        while not geo_iter.isDone():
            geo_iter.next()

    @classmethod
    def creator(cls):
        return MyDefomer()

    @classmethod
    def initialize(cls):
        pass


def initializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin, MyDefomer.VENDOR, MyDefomer.VERSION)
    try:
        plugin_fn.registerNode(
            MyDefomer.NODENAME, MyDefomer.NODEID, MyDefomer.creator, MyDefomer.initialize, ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: " + MyDefomer.NODENAME)


def uninitializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(MyDefomer.NODEID)
    except:
        om.MGlobal.displayError("Failed to deregister node: " + MyDefomer.NODENAME)


if __name__ == '__main__':
    """
    Just development 
    """
    plugin_file_name = "deformer_boilerplate.py"

    # a new scene is need because there mustn't be any created node when uninitialized the plugin
    mc.file(new=True, force=True)

    # unload + load
    if mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.unloadPlugin(plugin_file_name)
    if not mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.loadPlugin(plugin_file_name)

    # add a simply set up to test the defomer
    test_ply = mc.polySphere(name="C_test_PLY", constructionHistory=False)
    my_deformer = mc.deformer(test_ply, type=MyDefomer.NODENAME)
