# as there is no maya.OpenMaya import, there is no need to specify which is the API version
import maya.OpenMaya as om
from maya import OpenMayaMPx as ommpx


# Class definition
class MiniNode(ommpx.MPxNode):
    # Node definition
    VENDOR = 'Kike'
    VERSION = '1.0'
    NODE_NAME = "miniNode"
    NODE_ID = om.MTypeId(0x00118386)

    # create the placeholders to store the attributes handlers
    in1 = None
    in2 = None
    output = None

    def __init__(self):
        super(MiniNode, self).__init__()

    def compute(self, plug, data):
        """
        This method is the brain of the code, it's executed once for each dirty output value. So is important to filter
        the plug object for each output.
        It is in charge of recomputing the output based on the input values
        :param plug: (:obj: MObject): Contains the handle to the output plug
        :param data: (:obj: MDataBlock): Object that provides the interface to all the nodes values. It is only
        available during the compute method it cannot be stored in the class
        """
        if plug == MiniNode.output:
            # add the actions and the specific checks of the module
            # to get the input value data you must call the following function
            data.inputValue(MiniNode.in1).asFloat()

            # it is important to get the output handler, set the value and CLEAN the plug
            output_handle = data.outputValue(MiniNode.output)
            output_handle.setFloat(2)
            data.setClean(plug)
            return

        # as we use API 1.0 we have to send the result back
        return om.kUnknownParameter

    @staticmethod
    def create():
        """
        This method must always return a new instance of the node
        :return:
        """
        return ommpx.asMPxPtr(MiniNode())

    @staticmethod
    def initialize():
        """
        This method initialize all the attributes of the node, adds the attributes in the node, create its relations.
        This method is ONLY called when the plugin is loaded.

        Attributes can be created with several functions depending on their type MFnNumericAttribute, MFnTypedAttribute,
        MFnGenericAttribute and several more.
        The attributes can be:
            - readable: Can be used as a source of a dependency graph connections. Defaults to True
            - writable: Can be used as a destination of a dependency graph connection, and they are displayable in the
             attribute editor. Defaults to True
            - storable: Attribute is stored in the maya scene file. If the attribute can be recalculated with the
            information of the scene, it is better to set this flag to False, as they can be computed with existing data.
            Defaults to True
            - cached: Attribute is cached locally in the node data block, it fastened the speed of computation of the
             node, but it cost more memory. Defaults to True
            - keyable: Attribute appears in the channel box, and appears as an input in the node editor. Defaults to
            False
            - channelBox: Attribute appears in the channel box, and is no keyable. Defaults to False
            - hidden: Attribute hidden from the UI. They are not connectable. Defaults to False
            - array: Attribute supports an array as an input. Defaults to False

        """
        # Input
        n_attr = om.MFnNumericAttribute()
        MiniNode.in1 = n_attr.create("input1", "in1", om.MFnNumericData.kFloat, 1.0)
        n_attr.setStorable(True)
        n_attr.setKeyable(True)
        MiniNode.in2 = n_attr.create("input2", "in2", om.MFnNumericData.kFloat, 1.0)
        n_attr.setStorable(True)
        n_attr.setKeyable(True)

        # Output
        MiniNode.output = n_attr.create("output", "out", om.MFnNumericData.kFloat, 0.0)
        n_attr.setStorable(False)
        n_attr.setKeyable(False)
        n_attr.setWritable(False)

        # Add the new attributes to the node
        MiniNode.addAttribute(MiniNode.in1)
        MiniNode.addAttribute(MiniNode.in2)
        MiniNode.addAttribute(MiniNode.output)

        # Indicate that a particular input value affects the computation of a specified output value
        MiniNode.attributeAffects(MiniNode.in1, MiniNode.output)
        MiniNode.attributeAffects(MiniNode.in2, MiniNode.output)

    def postConstructor(self):
        """
        This method is called after the node is created, that is after the __innit__ method.
        Notice MPxNode methods cannot be called in the constructor.
        """
        pass

    # def connectionMade(self):
    #     """
    #     Method that is called when a connection is made into any attribute
    #     """
    #     pass
    #
    # def connectionBroken(self):
    #     """
    #     Method that is called when a connection is broken for an attribute
    #     """
    #     pass


# Initialize the scripted plug-in
def initializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin, MiniNode.VENDOR, MiniNode.VERSION)
    try:
        plugin_fn.registerNode(
            MiniNode.NODE_NAME, MiniNode.NODE_ID, MiniNode.create, MiniNode.initialize, ommpx.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: " + MiniNode.NODE_NAME)


# Uninitialize the scripted plug-in
def uninitializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(MiniNode.NODE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: " + MiniNode.NODE_NAME)


if __name__ == '__main__':
    """
    Just development 
    """
    import maya.cmds as mc

    plugin_file_name = "node_boilerplate1.py"

    # a new scene is need because there mustn't be any created node when uninitialized the plugin
    mc.file(new=True, force=True)

    # unload + load
    if mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.unloadPlugin(plugin_file_name)
    if not mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.loadPlugin(plugin_file_name)

    # add a simply set up to test the new node
    mc.createNode(MiniNode.NODE_NAME)
