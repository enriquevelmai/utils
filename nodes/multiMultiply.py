import sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

# Node definition
kPluginNodeName = "multiMultiply"
kPluginNodeId = OpenMaya.MTypeId(0x00118380)


# Class definition
class multiMultiply(OpenMayaMPx.MPxNode):
    inputs = OpenMaya.MObject()
    output = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == multiMultiply.output:

            input_handle = dataBlock.inputArrayValue(multiMultiply.inputs)
            if not input_handle.elementCount():
                return
            out = input_handle.inputValue().asFloat()
            count = input_handle.elementCount()
            for i in range(count - 1):
                input_handle.next()
                out *= input_handle.inputValue().asFloat()

            output_handle = dataBlock.outputValue(multiMultiply.output)
            output_handle.setFloat(out)
            dataBlock.setClean(plug)
            return
        return OpenMaya.kUnknownParameter


# Node creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(multiMultiply())


# Node initializer
def nodeInitializer():
    # Input
    n_attr = OpenMaya.MFnNumericAttribute()
    multiMultiply.inputs = n_attr.create("inputs", "in", OpenMaya.MFnNumericData.kFloat, 1.0)
    n_attr.setStorable(True)
    n_attr.setKeyable(True)
    n_attr.setArray(True)
    n_attr.setUsesArrayDataBuilder(True)

    # Output
    o_attr = OpenMaya.MFnNumericAttribute()
    multiMultiply.output = o_attr.create("output", "out", OpenMaya.MFnNumericData.kFloat, 0.0)
    o_attr.setStorable(False)
    o_attr.setKeyable(False)
    o_attr.setWritable(False)

    # Setup node attributes
    multiMultiply.addAttribute(multiMultiply.inputs)
    multiMultiply.addAttribute(multiMultiply.output)

    multiMultiply.attributeAffects(multiMultiply.inputs, multiMultiply.output)


# Initialize the scripted plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Kike", "1.0.0")
    try:
        mplugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write("Failed to register node: %s" % kPluginNodeName)
        raise


# Uninitialize the scripted plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % kPluginNodeName)
        raise
