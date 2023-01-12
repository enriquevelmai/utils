# as there is no maya.OpenMaya import, there is no need to specify which is the API version
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


# Class definition
class MyNode(om.MPxNode):
    # Node definition
    VENDOR = 'Kike'
    VERSION = '1.0'
    NODE_NAME = "myNode"
    NODE_ID = om.MTypeId(0x00118384)

    # create the placeholders to store the attributes handlers
    in1 = None
    in2 = None
    output = None

    def __init__(self):
        super(MyNode, self).__init__()

    def compute(self, plug, data):
        """
        This method is the brain of the code, it's executed once for each dirty output value. So is important to filter
        the plug object for each output.
        It is in charge of recomputing the output based on the input values
        :param plug: (:obj: MObject): Contains the handle to the output plug
        :param data: (:obj: MDataBlock): Object that provides the interface to all the nodes values. It is only
        available during the compute method it cannot be stored in the class
        """
        if plug == MyNode.output:
            # add the actions and the specific checks of the module
            # to get the input value data you must call the following function
            data.inputValue(MyNode.in1).asFloat()

            # it is important to get the output handler, set the value and CLEAN the plug
            output_handle = data.outputValue(MyNode.output)
            output_handle.setFloat(2)
            data.setClean(plug)

    @staticmethod
    def create():
        """
        This method must always return a new instance of the node
        :return:
        """
        return MyNode()

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

        In order to set ICONS to the node. There should be an image inside a MAYA_IMAGE_PATH with the name of the node.
            - For the node editor should be an image of 80x80 px under the name of myNode.png
            - For the outliner should be an image of 40x40 px with the prefix 'out_' under the name of out_myNode.png

        """
        # Input
        n_attr = om.MFnNumericAttribute()
        MyNode.in1 = n_attr.create("input1", "in1", om.MFnNumericData.kFloat, 1.0)
        n_attr.storable = True
        n_attr.keyable = True
        MyNode.in2 = n_attr.create("input2", "in2", om.MFnNumericData.kFloat, 1.0)
        n_attr.storable = True
        n_attr.keyable = True

        # Output
        MyNode.output = n_attr.create("output", "out", om.MFnNumericData.kFloat, 0.0)
        n_attr.storable = False
        n_attr.keyable = False
        n_attr.writable = False

        # Add the new attributes to the node
        MyNode.addAttribute(MyNode.in1)
        MyNode.addAttribute(MyNode.in2)
        MyNode.addAttribute(MyNode.output)

        # Indicate that a particular input value affects the computation of a specified output value
        MyNode.attributeAffects(MyNode.in1, MyNode.output)
        MyNode.attributeAffects(MyNode.in2, MyNode.output)

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
    plugin_fn = om.MFnPlugin(plugin, MyNode.VENDOR, MyNode.VERSION)
    try:
        plugin_fn.registerNode(
            MyNode.NODE_NAME, MyNode.NODE_ID, MyNode.create, MyNode.initialize, om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: " + MyNode.NODE_NAME)


# Uninitialize the scripted plug-in
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(MyNode.NODE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: " + MyNode.NODE_NAME)


if __name__ == '__main__':
    """
    Just development 
    """
    import maya.cmds as mc

    plugin_file_name = "node_boilerplate2.py"

    # a new scene is need because there mustn't be any created node when uninitialized the plugin
    mc.file(new=True, force=True)

    # unload + load
    if mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.unloadPlugin(plugin_file_name)
    if not mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.loadPlugin(plugin_file_name)

    # add a simply set up to test the new node
    mc.createNode(MyNode.NODE_NAME)
