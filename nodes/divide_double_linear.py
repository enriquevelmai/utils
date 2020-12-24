import sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

# Node definition
kPluginNodeName = "divideDoubleLinear"
kPluginNodeId = OpenMaya.MTypeId(0x00118381)


# Class definition
class divideDoubleLinear(OpenMayaMPx.MPxNode):
    in1 = OpenMaya.MObject()
    in2 = OpenMaya.MObject()
    output = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == divideDoubleLinear.output:

            in1_value = dataBlock.inputValue(divideDoubleLinear.in1).asFloat()
            in2_value = dataBlock.inputValue(divideDoubleLinear.in2).asFloat()

            if in2_value == 0:
                sys.stderr.write("C'mon, are you trying to divide by 0? You already know that answer!")
                raise BaseException()
            out = in1_value / float(in2_value)
            output_handle = dataBlock.outputValue(divideDoubleLinear.output)
            output_handle.setFloat(out)
            dataBlock.setClean(plug)
            return
        return OpenMaya.kUnknownParameter


# Node creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(divideDoubleLinear())


# Node initializer
def nodeInitializer():
    # Input
    n_attr1 = OpenMaya.MFnNumericAttribute()
    divideDoubleLinear.in1 = n_attr1.create("input1", "in1", OpenMaya.MFnNumericData.kFloat, 1.0)
    n_attr1.setStorable(True)
    n_attr1.setKeyable(True)
    n_attr2 = OpenMaya.MFnNumericAttribute()
    divideDoubleLinear.in2 = n_attr2.create("input2", "in2", OpenMaya.MFnNumericData.kFloat, 1.0)
    n_attr2.setStorable(True)
    n_attr2.setKeyable(True)

    # Output
    o_attr = OpenMaya.MFnNumericAttribute()
    divideDoubleLinear.output = o_attr.create("output", "out", OpenMaya.MFnNumericData.kFloat, 0.0)
    o_attr.setStorable(False)
    o_attr.setKeyable(False)
    o_attr.setWritable(False)

    # Setup node attributes
    divideDoubleLinear.addAttribute(divideDoubleLinear.in1)
    divideDoubleLinear.addAttribute(divideDoubleLinear.in2)
    divideDoubleLinear.addAttribute(divideDoubleLinear.output)

    divideDoubleLinear.attributeAffects(divideDoubleLinear.in1, divideDoubleLinear.output)
    divideDoubleLinear.attributeAffects(divideDoubleLinear.in2, divideDoubleLinear.output)


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
